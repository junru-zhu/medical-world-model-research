#!/usr/bin/env python3
"""Verified metadata corrections shared by review reference builders.

The canonical inclusion table preserves the frozen screening record.  This
module corrects publication metadata only at rendering time so that rebuilding
the reference ledger and BibTeX file cannot silently reintroduce known errors.
"""

from __future__ import annotations

from collections.abc import Mapping


REFERENCE_OVERRIDES: dict[str, dict[str, str]] = {
    "MWM-0117": {
        "authors": (
            "Ke Liu; Mengxuan Li; Yanyi Bao; Tianyun Zhang; Chong Chu; "
            "Jiajun Bu; Haishuai Wang"
        ),
    },
    "MWM-XA5E34A98D0": {
        "venue": "Frontiers in Artificial Intelligence",
        "volume": "4",
        "article_number": "798659",
        "entry_type": "article",
    },
    "MWM-X99717B78A9": {
        "authors": "Sitah Alharthi",
        "year": "2026",
        "venue": "Saudi Pharmaceutical Journal",
        "volume": "34",
        "issue": "1",
        "article_number": "1",
        "entry_type": "article",
    },
    "MWM-X531FFBB6AD": {
        "authors": "Clémence Métayer; Annabelle Ballesta; Julien Martinelli",
        "venue": "Briefings in Bioinformatics",
        "volume": "27",
        "issue": "1",
        "article_number": "bbaf722",
        "entry_type": "article",
    },
    "MWM-XA9B007D895": {
        "venue": "IEEE Access",
        "volume": "9",
        "pages": "105756--105775",
        "entry_type": "article",
    },
    "MWM-XD5F16C34AE": {
        "venue": "Human Brain Mapping",
        "volume": "47",
        "issue": "11",
        "article_number": "e70600",
        "entry_type": "article",
    },
    "MWM-X10E1E2640B": {
        "booktitle": (
            "2020 International Joint Conference on Neural Networks (IJCNN)"
        ),
        "venue": (
            "2020 International Joint Conference on Neural Networks (IJCNN)"
        ),
        "pages": "1--8",
        "entry_type": "inproceedings",
    },
    "MWM-0008": {
        "venue": "arXiv",
        "doi": "10.48550/arXiv.2605.23992",
        "entry_type": "misc",
    },
    "MWM-XB41D731350": {
        "venue": "medRxiv",
        "entry_type": "misc",
    },
    "MWM-0012": {
        "authors": (
            "Audrey Chan; Aaron Labbé; Jacob Lavoie; Jordan Bannister; "
            "Arsène Fansi Tchango; Guillaume Lajoie; Laurent Charlin"
        ),
    },
    "MWM-X6FB8E7370E": {
        "venue": "CPT: Pharmacometrics & Systems Pharmacology",
        "volume": "15",
        "issue": "5",
        "article_number": "e70258",
        "entry_type": "article",
    },
    "MWM-0239": {
        "authors": (
            "Tianxingjian Ding; Yuanhao Zou; Chen Chen; Mubarak Shah; Yu Tian"
        ),
        "title": (
            "CLARITY: Medical World Model for Guiding Treatment Decisions "
            "by Simulating Context-Aware Disease Trajectories in Latent Space"
        ),
        "year": "2026",
        "venue": "Computer Vision – ECCV 2026",
        "booktitle": "Computer Vision – ECCV 2026",
        "series": "Lecture Notes in Computer Science",
        "volume": "17076",
        "pages": "202--221",
        "doi": "10.1007/978-3-032-37038-9_12",
        "entry_type": "inproceedings",
    },
    "MWM-XD3411F7D18": {
        "authors": "Yann Maugé; Elias Ventre",
        "venue": "openRxiv",
        "entry_type": "misc",
    },
    "MWM-0294": {
        "venue": (
            "Medical Image Computing and Computer Assisted Intervention – "
            "MICCAI 2024"
        ),
        "booktitle": (
            "Medical Image Computing and Computer Assisted Intervention – "
            "MICCAI 2024"
        ),
        "series": "Lecture Notes in Computer Science",
        "volume": "15001",
        "pages": "190--199",
        "entry_type": "inproceedings",
    },
    "MWM-XC0A20D0271": {
        "authors": (
            "Yixuan Yang; Mehak Arora; Ryan Zhang; Baraa Abed; Junseob Kim; "
            "Tilendra Choudhary; Md Hassanuzzaman; Kevin Zhu; Ayman Ali; "
            "Chengkun Yang; Alasdair Edward Gent; Victor Moas; "
            "Rishikesan Kamaleswaran"
        ),
        "doi": "10.48550/arXiv.2605.10840",
    },
    "MWM-XA5A2F4844E": {
        "venue": "IEEE Transactions on Medical Robotics and Bionics",
        "volume": "4",
        "issue": "4",
        "pages": "945--956",
        "entry_type": "article",
    },
    "MWM-S004": {
        "authors": (
            "Yufan He; Pengfei Guo; Mengya Xu; Zhaoshuo Li; "
            "Andriy Myronenko; Dillan Imans; Bingjie Liu; Dongren Yang; "
            "Mingxue Gu; Yongnan Ji; Yueming Jin; Ren Zhao; Baiyong Shen; "
            "Daguang Xu"
        ),
    },
    "MWM-XD7F5DAFF27": {
        "venue": "IEEE Transactions on Visualization and Computer Graphics",
        "volume": "31",
        "issue": "1",
        "pages": "65--75",
        "entry_type": "article",
    },
    "MWM-XFA677C184B": {
        "authors": (
            "Weixin Liu; Juming Xiong; Congning Ni; Yanfan Zhu; Xingtao Lin; "
            "Bradley A. Malin; Zhijun Yin"
        ),
        "doi": "10.48550/arXiv.2607.25864",
    },
    "MWM-0369": {
        "venue": (
            "Proceedings of the Thirtieth International Joint Conference on "
            "Artificial Intelligence"
        ),
        "booktitle": (
            "Proceedings of the Thirtieth International Joint Conference on "
            "Artificial Intelligence"
        ),
        "pages": "507--513",
        "arxiv_id": "",
        "entry_type": "inproceedings",
    },
    "MWM-X2BD39C3B8E": {
        "venue": "Cyborg and Bionic Systems",
        "volume": "7",
        "article_number": "0559",
        "entry_type": "article",
    },
    "MWM-X872C154484": {
        "venue": "CPT: Pharmacometrics & Systems Pharmacology",
        "volume": "11",
        "issue": "3",
        "pages": "318--332",
        "entry_type": "article",
    },
    "MWM-X1305C7353F": {
        "venue": "npj Digital Medicine",
        "volume": "8",
        "issue": "1",
        "article_number": "80",
        "entry_type": "article",
    },
    "MWM-XF38CEA9063": {
        "venue": "npj Digital Medicine",
        "volume": "8",
        "issue": "1",
        "article_number": "596",
        "entry_type": "article",
    },
    "MWM-0242": {
        "venue": (
            "Proceedings of the IEEE/CVF Conference on Computer Vision and "
            "Pattern Recognition"
        ),
        "booktitle": (
            "Proceedings of the IEEE/CVF Conference on Computer Vision and "
            "Pattern Recognition"
        ),
        "pages": "25993--26003",
        "entry_type": "inproceedings",
    },
    "MWM-X056BF65776": {
        "venue": "bioRxiv",
        "entry_type": "misc",
    },
    "MWM-X6A64D732FB": {
        "venue": "Frontiers in Human Neuroscience",
        "volume": "19",
        "article_number": "1566566",
        "entry_type": "article",
    },
    "MWM-0261": {
        "authors": "Zhigang Tian",
        "venue": "Zenodo",
        "doi": "10.5281/zenodo.17609414",
        "note": "Version 1",
        "entry_type": "misc",
    },
    "MWM-XEA4B3285B2": {
        "venue": (
            "2025 47th Annual International Conference of the IEEE "
            "Engineering in Medicine and Biology Society (EMBC)"
        ),
        "booktitle": (
            "2025 47th Annual International Conference of the IEEE "
            "Engineering in Medicine and Biology Society (EMBC)"
        ),
        "pages": "1--7",
        "entry_type": "inproceedings",
    },
    "MWM-0125": {
        "venue": (
            "Proceedings of the IEEE/CVF Conference on Computer Vision and "
            "Pattern Recognition"
        ),
        "booktitle": (
            "Proceedings of the IEEE/CVF Conference on Computer Vision and "
            "Pattern Recognition"
        ),
        "pages": "1288--1299",
        "entry_type": "inproceedings",
    },
    "MWM-XC890A9B151": {
        "venue": "medRxiv",
        "arxiv_id": "",
        "entry_type": "misc",
    },
    "MWM-0263": {
        "authors": (
            "Yijun Yang; Zhao-Yang Wang; Qiuping Liu; Shuwen Sun; Kang Wang; "
            "Rama Chellappa; Zongwei Zhou; Alan Yuille; Lei Zhu; "
            "Yu-Dong Zhang; Jieneng Chen"
        ),
        "venue": (
            "2025 IEEE/CVF International Conference on Computer Vision "
            "(ICCV)"
        ),
        "booktitle": (
            "2025 IEEE/CVF International Conference on Computer Vision "
            "(ICCV)"
        ),
        "pages": "8319--8329",
        "entry_type": "inproceedings",
    },
    "MWM-X6C3AA8358E": {
        "venue": "Nature Machine Intelligence",
        "volume": "7",
        "issue": "7",
        "pages": "1076--1090",
        "entry_type": "article",
    },
    "MWM-X21155DF63C": {
        "venue": "Nature Machine Intelligence",
        "volume": "7",
        "issue": "9",
        "pages": "1478--1493",
        "entry_type": "article",
    },
    "MWM-X772584A789": {
        "year": "2022",
        "venue": "arXiv",
        "arxiv_id": "2009.04607",
        "url": "https://arxiv.org/abs/2009.04607",
        "entry_type": "misc",
    },
    "MWM-0136": {
        "authors": (
            "Javier Gamazo Tejero; Lukas Zbinden; Keyur Sheth; "
            "Raghavendra K M; Nadim Daher; Diego Granero Maraña; "
            "Filip Binkiewicz; Patrick Thornycroft; Mahdi Azizian; "
            "Sean D. Huver"
        ),
    },
    "MWM-0132": {
        "authors": (
            "Zijian Dong; Jianxiong Zhou; Kwun Kei Ng; "
            "Jan Paolo Macapinlac Balagtas; Zhizhou Li; Zijiao Chen; "
            "Juan Helen Zhou"
        ),
        "doi": "10.48550/arXiv.2608.01773",
    },
    "MWM-0135": {
        "venue": "Zenodo",
        "note": "Version 1.0.0, 5 May 2026",
        "entry_type": "misc",
    },
    "MWM-XBAD327876F": {
        "year": "2025",
        "venue": "Biomedical Engineering Advances",
        "volume": "10",
        "article_number": "100198",
        "doi": "10.1016/j.bea.2025.100198",
        "arxiv_id": "",
        "entry_type": "article",
    },
    "MWM-0138": {
        "authors": (
            "Open-H-Embodiment Consortium; Nigel Nelson; Juo-Tung Chen; "
            "Jesse Haworth; Xinhao Chen; Lukas Zbinden"
        ),
        "note": "Consortium-authored work; abbreviated author list",
    },
    "MWM-XB062A5A9FB": {
        "venue": "Nature Medicine",
        "volume": "29",
        "issue": "10",
        "pages": "2633--2642",
        "entry_type": "article",
    },
    "MWM-X7FD0DBDE79": {
        "venue": "npj Digital Medicine",
        "volume": "8",
        "issue": "1",
        "article_number": "220",
        "entry_type": "article",
    },
    "MWM-0157": {
        "authors": (
            "Sampath Rapuri; Lalithkumar Seenivasan; Dominik Schneider; "
            "Roger Soberanis-Mukul; Yufan He; Hao Ding; Jiru Xu; Chenhao Yu; "
            "Chenyan Jing; Pengfei Guo; Daguang Xu; Mathias Unberath"
        ),
    },
    "MWM-0177": {
        "authors": (
            "Ssharvien Kumar Sivakumar; Akwele Johnson; Anirudh Dhingra; "
            "Yannik Frisch; Ghazal Ghazaei; Anirban Mukhopadhyay"
        ),
    },
    "MWM-XC71FC75483": {
        "authors": (
            "Clément Abi Nader; Federica Ribaldi; Giovanni B. Frisoni; "
            "Valentina Garibotto; Philippe Robert; Nicholas Ayache; "
            "Marco Lorenzi"
        ),
        "venue": "Neurobiology of Aging",
        "volume": "113",
        "pages": "73--83",
        "entry_type": "article",
    },
    "MWM-XB6F8EC5868": {
        "venue": "Brain Communications",
        "volume": "3",
        "issue": "2",
        "article_number": "fcab091",
        "entry_type": "article",
    },
    "MWM-X9C071A2447": {
        "venue": (
            "Simulation, Image Processing, and Ultrasound Systems for "
            "Assisted Diagnosis and Navigation"
        ),
        "booktitle": (
            "Simulation, Image Processing, and Ultrasound Systems for "
            "Assisted Diagnosis and Navigation"
        ),
        "series": "Lecture Notes in Computer Science",
        "volume": "15186",
        "pages": "58--67",
        "doi": "10.1007/978-3-031-73647-6_6",
        "entry_type": "inproceedings",
    },
    "MWM-0174": {
        "authors": (
            "Wentao Pan; Wuyang Li; Shengyuan Liu; Xinyu Liu; Hengyu Liu; "
            "Yixuan Yuan"
        ),
    },
    "MWM-S006": {
        "venue": "CVPR 2026 Findings",
        "booktitle": "CVPR 2026 Findings",
        "pages": "5315--5324",
        "entry_type": "inproceedings",
    },
    "MWM-S005": {
        "venue": (
            "Data Engineering in Medical Imaging, Machine Learning in "
            "Medical Imaging, and Clinical Image-Based Procedures"
        ),
        "booktitle": (
            "Data Engineering in Medical Imaging, Machine Learning in "
            "Medical Imaging, and Clinical Image-Based Procedures"
        ),
        "series": "Lecture Notes in Computer Science",
        "volume": "16191",
        "pages": "1--10",
        "doi": "10.1007/978-3-032-08009-7_1",
        "year": "2026",
        "entry_type": "inproceedings",
    },
    "MWM-XCC1C1352D9": {
        "venue": "medRxiv",
        "entry_type": "misc",
    },
    "MWM-0199": {
        "note": "Manuscript submitted to IROS; acceptance not verified",
    },
    "MWM-X009A6E0F91": {
        "venue": (
            "IEEE Transactions on Pattern Analysis and Machine Intelligence"
        ),
        "volume": "45",
        "issue": "11",
        "pages": "13363--13375",
        "entry_type": "article",
    },
    "MWM-X5E3C456867": {
        "venue": "arXiv preprint",
        "doi": "10.48550/arXiv.2608.20284",
        "entry_type": "misc",
    },
    "MWM-0114": {
        "venue": (
            "Proceedings of the 32nd ACM SIGKDD Conference on Knowledge "
            "Discovery and Data Mining V.1"
        ),
        "booktitle": (
            "Proceedings of the 32nd ACM SIGKDD Conference on Knowledge "
            "Discovery and Data Mining V.1"
        ),
        "year": "2026",
        "pages": "1693--1704",
        "publisher": "ACM",
        "arxiv_id": "2505.19785",
        "entry_type": "inproceedings",
    },
    "MWM-0315": {
        "authors": (
            "Hongbin Lin; Bin Li; Chun Wai Wong; Juan Rojas; Xiangyu Chu; "
            "Kwok Wai Samuel Au"
        ),
        "venue": "Robotics: Science and Systems XX",
        "booktitle": "Robotics: Science and Systems XX",
        "year": "2024",
        "doi": "10.15607/RSS.2024.XX.041",
        "entry_type": "inproceedings",
    },
    "MWM-S003": {
        "authors": (
            "Qinghui Liu; Elies Fuster-Garcia; Ivar Thokle Hovden; "
            "Bradley J. MacIntosh; Edvard O. S. Grødem; Petter Brandal; "
            "Carles Lopez-Mateu; Donatas Sederevičius; Karoline Skogen; "
            "Till Schellhorn; Atle Bjørnerud; Kyrre Eeg Emblem"
        ),
        "venue": "IEEE Transactions on Medical Imaging",
        "year": "2025",
        "volume": "44",
        "issue": "6",
        "pages": "2449--2462",
        "doi": "10.1109/TMI.2025.3533038",
        "arxiv_id": "",
        "entry_type": "article",
    },
    "MWM-X2E0B832A46": {
        "venue": "CPT: Pharmacometrics & Systems Pharmacology",
        "volume": "13",
        "issue": "8",
        "pages": "1309--1316",
        "entry_type": "article",
    },
    "MWM-0215": {
        "venue": "AI Medicine",
        "volume": "3",
        "issue": "1",
        "article_number": "2",
        "entry_type": "article",
    },
    "MWM-0290": {
        "authors": (
            "Zefan Yang; Ge Wang; James Hendler; Mannudeep K. Kalra; "
            "Pingkun Yan"
        ),
        "year": "2026",
        "venue": (
            "Proceedings of the IEEE/CVF Conference on Computer Vision and "
            "Pattern Recognition"
        ),
        "booktitle": (
            "Proceedings of the IEEE/CVF Conference on Computer Vision and "
            "Pattern Recognition"
        ),
        "pages": "6920--6930",
        "url": (
            "https://openaccess.thecvf.com/content/CVPR2026/html/"
            "Yang_X-WIN_Building_Chest_Radiograph_World_Model_via_"
            "Predictive_Sensing_CVPR_2026_paper.html"
        ),
        "entry_type": "inproceedings",
    },
    "MWM-S002": {
        "authors": (
            "Zefan Yang; Xinrui Song; Xuanang Xu; Yongyi Shi; Ge Wang; "
            "Mannudeep K. Kalra; Pingkun Yan"
        ),
        "venue": "arXiv preprint",
        "doi": "10.48550/arXiv.2506.19055",
        "entry_type": "misc",
    },
}


def apply_reference_override(row: Mapping[str, str]) -> dict[str, str]:
    """Return a copy of *row* with verified rendering metadata applied."""

    merged = dict(row)
    merged.update(REFERENCE_OVERRIDES.get(row["candidate_id"], {}))
    return merged
