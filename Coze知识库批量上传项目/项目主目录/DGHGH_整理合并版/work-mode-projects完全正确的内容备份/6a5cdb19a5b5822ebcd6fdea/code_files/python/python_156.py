logging.basicConfig(
       level=logging.INFO,
       handlers=[
           logging.FileHandler("ai_training.log"),
           logging.StreamHandler()
       ]
   )