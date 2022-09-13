## Metainformation Extraction from Encrypted Streaming Video Packet Traces

Here is experimental code for extracting and identifying title, series title and film/series genre from encrypted streaming video packet traces.

## Usage

### Datasets

To build the datasets you need to use the following source files:
* **Netflix**: You can download the original dataset there: https://drive.google.com/drive/folders/0B3cMrOhPT_6zOUNYNUdEN0ZFXzA?resourcekey=0-uh6TIA_pwOrRz9HlvEht9g
  - Reference: * Andrew Reed and Michael Kranch. Identifying https-protected netflix
videos in real-time. In Proceedings of the Seventh ACM on Conference
on Data and Application Security and Privacy, pages 361–368, 2017 *
* **SVT**: You can download the original dataset there: https://drive.google.com/file/d/13ez6D9axWs-F-0xiHMnl91VI_pqr-grf/view?usp=sharing
  - Reference: * Philip Antonsson, Martin Björklund, Tobias Hjalmarsson, Marcus Julin,
Andreas Stenwreth, and Malte  Åkvist. Streaming video identification. Bachelor’s Thesis, Chalmers University of Technology, 2022 *

Once downloaded in the same folder, you can generate the metainformation databases as follows:
```sh
cd src
python3 read.py
python3 svt.py
```

### Files and Test

* `learner.py`: simple SVM learner for title, series and genres (One-Versus-All, All-Versus-All) recognition.
* `chunk_learner.py`: do the same job as learner but splitting the database into * n * chunks.
* `read.py`: utilities to parse and build the metainformation database for netflix.
* `svt.py`: learner and database building for the svt dataset.
* `test.py`: simple tests of the learner classes.
* `plots.py`: generate plots for the paper.

Once you have built all necessary files, you can run the tests by issueing the following command:
```sh
cd src
python3 test.py
```
   
### Python Dependencies

sklearn, numpy, matplotlib

## Cite

Please cite the following publication:

`Romaric Duvignau. Metainformation Extraction from Encrypted Streaming Video Packet Traces. Proc. of the International Conference on Electrical, Computer, Communications and Mechatronics Engineering (ICECCME)
16-18 November 2022, To be published.`

## Contact

Romaric Duvignau, duvignau@chalmers.se.
