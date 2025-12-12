# Machina Emblematica
This repository contains code experiments done in context of the Machina Emblematica project. The goal was to implement a simple state of the art Retrieval Augmented Generation (RAG) system that makes the digital 1668 edition of Joachim Camerarius’ [Symbola et Emblemata](https://www.digitale-sammlungen.de/en/details/bsb10575861) more accessible and explorable. The team published an innovative, user-friendly chatbot prototype that enables users to ask questions about the emblems and search for related contents in the Symbola et Emblemata. Machina Emblematica innovates access and exploration of the 17th century Latin emblems by providing an assistant that generates user query responses in English based on the most relevant multimodal content retrieved. The prototype advances existing solutions from projects enhancing accessibility and exploration of historical images and texts.

## Documentation
**Multimodal Search Backend:** The */src* folder contains the code used to preprocess the images and texts (*image_metadata.py, extract_text_chunks.py*) and to index the multimodal contents with Marqo (*index_images.py, index_text.py*).
**RAG System**: The Jupyter notebook (*Machina Emblematica Agentic RAG Tests.ipynb*) contains Python code experiments done in context of the Machina Emblematica project. Most of the workflow and logic were integrated into the browser tool, which can be tested here: [https://machina.rainersimon.io/](https://machina.rainersimon.io/). The sourcecode is available here: [https://github.com/rsimon/machina-emblematica](https://github.com/rsimon/machina-emblematica).

## Funding Acknowledgement
This project received funding from the BMFTR joint project HERMES and the Furman Humanities Center.

# References
```
@misc{vignoli_2025_17909191,
  author       = {Vignoli, Michela and
                  Simon, Rainer},
  title        = {Machina Emblematica: Multimodal Information
                   Retrieval Prototype for CH and DH
                  },
  month        = dec,
  year         = 2025,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.17909191},
  url          = {https://doi.org/10.5281/zenodo.17909191},
}
```
