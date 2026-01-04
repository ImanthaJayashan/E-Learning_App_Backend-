# Train/data — Image Dataset

This folder contains the image dataset organized by letter class. Each subfolder corresponds to one class used for training and inference.

Allowed classes (folders included):

- A
- B
- C
- D
- E
- F
- G
- H
- J
- L
- N
- O
- P
- R
- S
- U
- V

Structure

`data/<LETTER>/` — contains image files for the given letter. These are the input images used by `Train/train.py` (via `torchvision.datasets.ImageFolder`).

How this is generated

`map.py` reads `english.csv` and copies image files into the appropriate `data/<LETTER>/` folder for the allowed letters. Ensure the CSV's `image` paths are accessible when running `map.py`.

If you want READMEs inside each class folder, see the generated per-class README files.