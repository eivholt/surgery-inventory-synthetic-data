import time
import asyncio
import json
import io
import carb
import logging
import omni.kit
import omni.usd
import omni.replicator.core as rep
from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch

logger = logging.getLogger(__name__)
logger.info("Logging with 'logging'")
carb.log_info("Logging with 'carb'")
rep.settings.carb_settings("/omni/replicator/RTSubframes", 1) #If randomizing materials leads to problems, try value 3

with rep.new_layer():
	def scatter_items(items):
		table = rep.get.prims(path_pattern='/World/SurgeryToolsArea')
		with items as item:
			carb.log_info("Tool: " + str(tool))
			logger.info("Tool: " + str(tool))
			rep.modify.pose(rotation=rep.distribution.uniform((0, 0, 0), (0, 360, 0)))
			rep.randomizer.scatter_2d(surface_prims=table, check_for_collisions=True)
		return items.node
	
	def randomize_camera():
		with camera:
			rep.modify.pose(
				position=rep.distribution.uniform((-10, 50, 50), (10, 120, 90)),
				look_at=(0, 0, 0))
		return camera
	
	def alternate_lights():
		with lights:
			rep.modify.attribute("intensity", rep.distribution.uniform(10000, 90000))
		return lights.node


	rep.settings.set_render_pathtraced(samples_per_pixel=64)
	camera = rep.create.camera(position=(0, 24, 0))
	tools = rep.get.prims(semantics=[("class", "tweezers"), ("class", "scissors"), ("class", "scalpel"), ("class", "sponge")])
	backgrounditems = rep.get.prims(semantics=[("class", "background")])
	lights = rep.get.light(semantics=[("class", "spotlight")])
	render_product = rep.create.render_product(camera, (128, 128))

	rep.randomizer.register(scatter_items)
	rep.randomizer.register(randomize_camera)
	rep.randomizer.register(alternate_lights)
     
	with rep.trigger.on_frame(num_frames=10000, rt_subframes=20):
		rep.randomizer.scatter_items(tools)
		rep.randomizer.randomize_camera()
		rep.randomizer.alternate_lights()

	writer = rep.WriterRegistry.get("BasicWriter")
	writer.initialize(
		output_dir="C:/Users/eivho/source/repos/surgery-inventory/Dataset/omniverse-replicator/out2",
		rgb=True,
		bounding_box_2d_tight=True)

	writer.attach([render_product])
	asyncio.ensure_future(rep.orchestrator.step_async())