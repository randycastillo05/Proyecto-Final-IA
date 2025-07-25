import gradio as gr
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import pipeline, AutoModel, AutoTokenizer
import numpy as np
import librosa
import soundfile as sf
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import json