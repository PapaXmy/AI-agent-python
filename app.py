import argparse

from config import settings
from embeddings import get_embeddings
from interface_gradio import chat
from loaders import load_documents
from vector_store import get_vector_store


def main():
