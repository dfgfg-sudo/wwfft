from core.training_engine import TrainingEngine
config = TrainingConfig(batch_size=32, epochs=50)
engine = TrainingEngine(model, config)
engine.train(train_loader, val_loader)