"""Probabilistic clinical-dynamics model implementations."""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor, nn


@dataclass
class ForecastOutput:
    mean: Tensor
    log_scale: Tensor
    mask_logits: Tensor
    kl: Tensor | None = None


def bounded_log_scale(raw: Tensor) -> Tensor:
    """Keep Gaussian scales finite without hard clipping gradients."""
    return -5.0 + 7.0 * torch.sigmoid(raw)


class GRUDProbabilistic(nn.Module):
    """GRU-D with trainable input/hidden decay and probabilistic heads."""

    def __init__(self, variables: int, hidden_size: int = 96) -> None:
        super().__init__()
        self.variables = variables
        self.hidden_size = hidden_size
        self.input_decay = nn.Linear(variables, variables)
        self.hidden_decay = nn.Linear(variables, hidden_size)
        self.cell = nn.GRUCell(variables * 3 + 1, hidden_size)
        self.value_head = nn.Linear(hidden_size, variables * 2)
        self.mask_head = nn.Linear(hidden_size, variables)

    def initial_state(self, batch_size: int, device: torch.device) -> Tensor:
        return torch.zeros(batch_size, self.hidden_size, device=device)

    def step(
        self,
        values: Tensor,
        masks: Tensor,
        deltas: Tensor,
        time: Tensor,
        hidden: Tensor,
    ) -> tuple[ForecastOutput, Tensor]:
        gamma_x = torch.exp(-torch.relu(self.input_decay(deltas)))
        gamma_h = torch.exp(-torch.relu(self.hidden_decay(deltas)))
        effective_values = masks * values + (1.0 - masks) * gamma_x * values
        hidden = gamma_h * hidden
        hidden = self.cell(
            torch.cat([effective_values, masks, deltas, time], dim=-1),
            hidden,
        )
        value_parameters = self.value_head(hidden)
        mean, raw_scale = value_parameters.chunk(2, dim=-1)
        output = ForecastOutput(
            mean=mean,
            log_scale=bounded_log_scale(raw_scale),
            mask_logits=self.mask_head(hidden),
        )
        return output, hidden

    def forward(
        self,
        values: Tensor,
        masks: Tensor,
        deltas: Tensor,
        time: Tensor,
    ) -> ForecastOutput:
        batch_size, steps, _ = values.shape
        hidden = self.initial_state(batch_size, values.device)
        means: list[Tensor] = []
        log_scales: list[Tensor] = []
        mask_logits: list[Tensor] = []
        for index in range(steps):
            output, hidden = self.step(
                values[:, index],
                masks[:, index],
                deltas[:, index],
                time[:, index],
                hidden,
            )
            means.append(output.mean)
            log_scales.append(output.log_scale)
            mask_logits.append(output.mask_logits)
        return ForecastOutput(
            mean=torch.stack(means, dim=1),
            log_scale=torch.stack(log_scales, dim=1),
            mask_logits=torch.stack(mask_logits, dim=1),
        )


class CausalTransformerProbabilistic(nn.Module):
    """Causal Transformer with Gaussian value and Bernoulli mask heads."""

    def __init__(
        self,
        variables: int,
        d_model: int = 128,
        layers: int = 3,
        heads: int = 4,
        feedforward: int = 256,
        dropout: float = 0.1,
        maximum_length: int = 512,
    ) -> None:
        super().__init__()
        self.variables = variables
        self.d_model = d_model
        self.maximum_length = maximum_length
        self.input_projection = nn.Linear(variables * 3 + 1, d_model)
        self.position = nn.Parameter(torch.zeros(1, maximum_length, d_model))
        nn.init.normal_(self.position, std=0.02)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=heads,
            dim_feedforward=feedforward,
            dropout=dropout,
            batch_first=True,
            norm_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=layers)
        self.normalization = nn.LayerNorm(d_model)
        self.value_head = nn.Linear(d_model, variables * 2)
        self.mask_head = nn.Linear(d_model, variables)

    def output_heads(self, hidden: Tensor) -> ForecastOutput:
        hidden = self.normalization(hidden)
        value_parameters = self.value_head(hidden)
        mean, raw_scale = value_parameters.chunk(2, dim=-1)
        return ForecastOutput(
            mean=mean,
            log_scale=bounded_log_scale(raw_scale),
            mask_logits=self.mask_head(hidden),
        )

    def initialize_cache(
        self,
        values: Tensor,
        masks: Tensor,
        deltas: Tensor,
        time: Tensor,
    ) -> tuple[ForecastOutput, list[Tensor]]:
        """Run a causal context once and cache each layer's normalized keys."""
        steps = values.shape[1]
        if steps > self.maximum_length:
            raise ValueError(
                f"Sequence length {steps} exceeds maximum {self.maximum_length}"
            )
        features = torch.cat([values, masks, deltas, time], dim=-1)
        hidden = self.input_projection(features) * math.sqrt(self.d_model)
        hidden = hidden + self.position[:, :steps]
        causal_mask = torch.triu(
            torch.ones(steps, steps, device=values.device, dtype=torch.bool),
            diagonal=1,
        )
        caches: list[Tensor] = []
        for layer in self.encoder.layers:
            normalized = layer.norm1(hidden)
            caches.append(normalized)
            attention = layer.self_attn(
                normalized,
                normalized,
                normalized,
                attn_mask=causal_mask,
                need_weights=False,
            )[0]
            hidden = hidden + layer.dropout1(attention)
            hidden = hidden + layer._ff_block(layer.norm2(hidden))
        return self.output_heads(hidden), caches

    def cached_step(
        self,
        values: Tensor,
        masks: Tensor,
        deltas: Tensor,
        time: Tensor,
        *,
        position_index: int,
        caches: list[Tensor],
    ) -> tuple[ForecastOutput, list[Tensor]]:
        """Append one causal token using exact per-layer key/value caches."""
        if position_index >= self.maximum_length:
            raise ValueError(
                f"Position {position_index} exceeds maximum "
                f"{self.maximum_length - 1}"
            )
        features = torch.cat([values, masks, deltas, time], dim=-1).unsqueeze(1)
        hidden = self.input_projection(features) * math.sqrt(self.d_model)
        hidden = hidden + self.position[:, position_index : position_index + 1]
        updated_caches: list[Tensor] = []
        for layer, cache in zip(self.encoder.layers, caches, strict=True):
            normalized = layer.norm1(hidden)
            key_value = torch.cat([cache, normalized], dim=1)
            attention = layer.self_attn(
                normalized,
                key_value,
                key_value,
                need_weights=False,
            )[0]
            hidden = hidden + layer.dropout1(attention)
            hidden = hidden + layer._ff_block(layer.norm2(hidden))
            updated_caches.append(key_value)
        return self.output_heads(hidden), updated_caches

    def forward(
        self,
        values: Tensor,
        masks: Tensor,
        deltas: Tensor,
        time: Tensor,
        padding_mask: Tensor | None = None,
    ) -> ForecastOutput:
        steps = values.shape[1]
        if steps > self.maximum_length:
            raise ValueError(
                f"Sequence length {steps} exceeds maximum {self.maximum_length}"
            )
        features = torch.cat([values, masks, deltas, time], dim=-1)
        hidden = self.input_projection(features) * math.sqrt(self.d_model)
        hidden = hidden + self.position[:, :steps]
        causal_mask = torch.triu(
            torch.ones(steps, steps, device=values.device, dtype=torch.bool),
            diagonal=1,
        )
        hidden = self.encoder(
            hidden,
            mask=causal_mask,
            src_key_padding_mask=padding_mask,
        )
        return self.output_heads(hidden)


class RecurrentStateSpaceModel(nn.Module):
    """Stochastic recurrent state-space model with value and mask decoders."""

    def __init__(
        self,
        variables: int,
        hidden_size: int = 96,
        latent_size: int = 32,
    ) -> None:
        super().__init__()
        self.variables = variables
        self.hidden_size = hidden_size
        self.latent_size = latent_size
        self.transition = nn.GRUCell(
            variables * 3 + 1 + latent_size,
            hidden_size,
        )
        self.prior = nn.Linear(hidden_size, latent_size * 2)
        self.posterior = nn.Linear(
            hidden_size + variables * 2,
            latent_size * 2,
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_size + latent_size, hidden_size),
            nn.SiLU(),
        )
        self.value_head = nn.Linear(hidden_size, variables * 2)
        self.mask_head = nn.Linear(hidden_size, variables)

    def initial_state(
        self, batch_size: int, device: torch.device
    ) -> tuple[Tensor, Tensor]:
        hidden = torch.zeros(batch_size, self.hidden_size, device=device)
        latent = torch.zeros(batch_size, self.latent_size, device=device)
        return hidden, latent

    @staticmethod
    def distribution(parameters: Tensor) -> tuple[Tensor, Tensor]:
        mean, raw_log_scale = parameters.chunk(2, dim=-1)
        log_scale = -5.0 + 6.0 * torch.sigmoid(raw_log_scale)
        return mean, log_scale

    @staticmethod
    def sample(mean: Tensor, log_scale: Tensor) -> Tensor:
        if mean.requires_grad:
            return mean + torch.randn_like(mean) * torch.exp(log_scale)
        return mean

    @staticmethod
    def gaussian_kl(
        posterior_mean: Tensor,
        posterior_log_scale: Tensor,
        prior_mean: Tensor,
        prior_log_scale: Tensor,
    ) -> Tensor:
        posterior_var = torch.exp(2.0 * posterior_log_scale)
        prior_var = torch.exp(2.0 * prior_log_scale)
        return (
            prior_log_scale
            - posterior_log_scale
            + (posterior_var + (posterior_mean - prior_mean).square())
            / (2.0 * prior_var)
            - 0.5
        ).sum(dim=-1)

    def transition_step(
        self,
        values: Tensor,
        masks: Tensor,
        deltas: Tensor,
        time: Tensor,
        hidden: Tensor,
        previous_latent: Tensor,
    ) -> tuple[Tensor, Tensor, Tensor]:
        hidden = self.transition(
            torch.cat(
                [values, masks, deltas, time, previous_latent],
                dim=-1,
            ),
            hidden,
        )
        prior_mean, prior_log_scale = self.distribution(self.prior(hidden))
        return hidden, prior_mean, prior_log_scale

    def decode(
        self, hidden: Tensor, latent: Tensor
    ) -> ForecastOutput:
        decoded = self.decoder(torch.cat([hidden, latent], dim=-1))
        value_parameters = self.value_head(decoded)
        mean, raw_scale = value_parameters.chunk(2, dim=-1)
        return ForecastOutput(
            mean=mean,
            log_scale=bounded_log_scale(raw_scale),
            mask_logits=self.mask_head(decoded),
        )

    def forward(
        self,
        values: Tensor,
        masks: Tensor,
        deltas: Tensor,
        time: Tensor,
        next_observed_values: Tensor,
        next_masks: Tensor,
    ) -> ForecastOutput:
        batch_size, steps, _ = values.shape
        hidden, latent = self.initial_state(batch_size, values.device)
        means: list[Tensor] = []
        log_scales: list[Tensor] = []
        mask_logits: list[Tensor] = []
        kl_values: list[Tensor] = []
        for index in range(steps):
            hidden, prior_mean, prior_log_scale = self.transition_step(
                values[:, index],
                masks[:, index],
                deltas[:, index],
                time[:, index],
                hidden,
                latent,
            )
            posterior_parameters = self.posterior(
                torch.cat(
                    [
                        hidden,
                        next_observed_values[:, index],
                        next_masks[:, index],
                    ],
                    dim=-1,
                )
            )
            posterior_mean, posterior_log_scale = self.distribution(
                posterior_parameters
            )
            latent = self.sample(posterior_mean, posterior_log_scale)
            output = self.decode(hidden, latent)
            means.append(output.mean)
            log_scales.append(output.log_scale)
            mask_logits.append(output.mask_logits)
            kl_values.append(
                self.gaussian_kl(
                    posterior_mean,
                    posterior_log_scale,
                    prior_mean,
                    prior_log_scale,
                )
            )
        return ForecastOutput(
            mean=torch.stack(means, dim=1),
            log_scale=torch.stack(log_scales, dim=1),
            mask_logits=torch.stack(mask_logits, dim=1),
            kl=torch.stack(kl_values, dim=1),
        )


def build_model(
    name: str,
    variables: int,
    *,
    hidden_size: int,
    latent_size: int,
    transformer_layers: int,
    transformer_heads: int,
    dropout: float,
    maximum_length: int,
) -> nn.Module:
    if name == "grud":
        return GRUDProbabilistic(variables, hidden_size=hidden_size)
    if name == "transformer":
        return CausalTransformerProbabilistic(
            variables,
            d_model=hidden_size,
            layers=transformer_layers,
            heads=transformer_heads,
            feedforward=hidden_size * 2,
            dropout=dropout,
            maximum_length=maximum_length,
        )
    if name == "rssm":
        return RecurrentStateSpaceModel(
            variables,
            hidden_size=hidden_size,
            latent_size=latent_size,
        )
    raise ValueError(f"Unknown model: {name}")
