## Metainformation Extraction from Encrypted Streaming Video Packet Traces

Here is experimental code for extracting and identifying title, series title and film/series genre from encrypted streaming video packet traces.

## Usage

### Datasets

To build the datasets you need to use the following source files:
* **Netflix**: You can download the original dataset there: https://drive.google.com/drive/folders/0B3cMrOhPT_6zOUNYNUdEN0ZFXzA?resourcekey=0-uh6TIA_pwOrRz9HlvEht9g
  - Reference: _Andrew Reed and Michael Kranch. Identifying https-protected netflix
videos in real-time. In Proceedings of the Seventh ACM on Conference
on Data and Application Security and Privacy, pages 361–368, 2017._
* **SVT**: You can download the original dataset there: https://drive.google.com/file/d/13ez6D9axWs-F-0xiHMnl91VI_pqr-grf/view?usp=sharing (updated datasets, and also including only videos accessible outside Sweden can be accessed there: https://github.com/embeage/streaming-identification)
  - Reference: _M. Björklund, M. Julin, P. Antonsson, A. Stenwreth, M. Åkvist, T. Hjalmarsson, and R. Duvignau, “I see what you’re watching on your streaming service: Fast identification of dash encrypted network traces,” in 2023 20th IEEE Annual Consumer Communication & Networking Conference (CCNC). IEEE, 2023, pp. 1116-1122._

Once downloaded in the same folder, you can generate the metainformation databases as follows:
```sh
cd metaextract
python3 read.py
python3 svt.py
```

### Files and Tests

* `learner.py`: simple SVM learner for title, series and genres (One-Versus-All, All-Versus-All) recognition.
* `chunk_learner.py`: do the same job as learner but splitting the database into *n* chunks.
* `read.py`: utilities to parse and build the metainformation database for netflix.
* `svt.py`: learner and database building for the svt dataset.
* `test.py`: simple tests of the learner classes.
* `plots.py`: generate plots for the paper.

Once you have built all necessary files, you can run the tests by issueing the following command:
```sh
cd metaextract
python3 test.py
```
   
### Python Dependencies

sklearn, numpy, matplotlib

## Cite

If used, please cite the following publication:

_Romaric Duvignau. Metainformation Extraction from Encrypted Streaming Video Packet Traces. Proc. of the International Conference on Electrical, Computer, Communications and Mechatronics Engineering (ICECCME), 16-18 November 2022, pp. 1-6._

## Contact

Romaric Duvignau, duvignau@chalmers.se.
