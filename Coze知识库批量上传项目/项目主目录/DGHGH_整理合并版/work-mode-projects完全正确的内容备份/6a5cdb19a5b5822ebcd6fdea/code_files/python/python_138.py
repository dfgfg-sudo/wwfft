import asyncio
   from neurofactory_fusion import NeuroFactoryFusionSystem
   
   async def run():
       system = NeuroFactoryFusionSystem()
       await system.initialize()
       result = await system.execute_ai_training({'data_path': './data/train'})
       print(result)
   asyncio.run(run())