from Rag.EmbeddingsAndVectorStore import EmbbeddingsAndIndexing
from Configuration import Test_Conncection_To_Gemini

Test= Test_Conncection_To_Gemini()

if Test:
    EmbbeddingsAndIndexing("hi there first try working woth new embeddignd engine")