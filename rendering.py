import bpy
import math
import random
import os
from mathutils import Vector, Euler
import json


# Set the number of frames per folder
frames_per_folder = 1000

# Starting folder number (change this)
starting_folder_number = 5




# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set render engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'

# Set device to GPU
bpy.context.scene.cycles.device = 'GPU'

# Enable all available GPUs
bpy.context.preferences.addons['cycles'].preferences.get_devices()
for d in bpy.context.preferences.addons['cycles'].preferences.devices:
    d.use = True

# Optionally, set tile size for GPU rendering (e.g. 256x256)
bpy.context.scene.cycles.tile_x = 1024
bpy.context.scene.cycles.tile_y = 1024

# Set maximum bounces for the Cycles renderer
bpy.context.scene.cycles.max_bounces = 36  # Set a higher value (default is 12)

# Set diffuse bounces (light bouncing off surfaces)
bpy.context.scene.cycles.diffuse_bounces = 12  # Increase for more light scattering (default is 4)

# Set specular bounces (light reflections on shiny surfaces)
bpy.context.scene.cycles.specular_bounces = 12  # Increase for better reflections (default is 8)

# Set transmission bounces (light passing through transparent materials)
bpy.context.scene.cycles.transmission_bounces = 12  # Increase for more refraction (default is 12)

# Set volume bounces (light scattering in volumes like smoke or fog)
bpy.context.scene.cycles.volume_bounces = 2  # Increase for more volume interaction (default is 2)

# Optional: You can also increase the number of light paths for better light sampling
bpy.context.scene.cycles.samples = 1024 # Increase samples for higher quality renders (default is 128)


def check_gpu_usage():
    if bpy.context.scene.cycles.device == 'GPU':
        print("GPU rendering is enabled.")
    else:
        print("GPU rendering is not enabled.")

# Check GPU usage before rendering
check_gpu_usage()

# Create room (with top and taller walls)
def create_room():
    # Define vertices for the room, now with a top
    verts = [
        (1, 1, 0),  (1, -1, 0),  (-1, -1, 0),  (-1, 1, 0),  # Bottom floor
        (1, 1, 7),  (1, -1, 7),  (-1, -1, 7),  (-1, 1, 7),  # Top floor (height = 7)
    ]
    
    # Define faces for the room (without a top initially)
    faces = [
        (0, 1, 2, 3),  # Bottom face
        (0, 4, 5, 1),  # Front wall
        (1, 5, 6, 2),  # Right wall
        (2, 6, 7, 3),  # Back wall
        (3, 7, 4, 0),  # Left wall
        (4, 5, 6, 7)   # Top face (added to close the room)
    ]
    
    # Create mesh and object for the room
    mesh = bpy.data.meshes.new("Room")
    obj = bpy.data.objects.new("Room", mesh)
    
    # Link the object to the scene
    bpy.context.collection.objects.link(obj)
    
    # Create the mesh from the vertex and face data
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Scale the object to increase size of room
    obj.scale = (10, 10, 7)  # Larger room size, and taller walls (height = 7)
    
    return obj

# Create the room
room = create_room()





# Function to create a realistic material 
def create_realistic_material():
    material_type = random.choice(['Metal', 'Plastic', 'Wood', 'Glass', 'Stone'])
    mat = bpy.data.materials.new(name=f"Realistic_{material_type}")
    mat.use_nodes = True  # Enable node-based material
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    if material_type == 'Metal':
        # Metal Material
        bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)  # Light gray metal
        bsdf.inputs['Metallic'].default_value = 1  # Fully metallic
        bsdf.inputs['Roughness'].default_value = 0.2  # Slightly rough for a more realistic look
    
    elif material_type == 'Plastic':
        # Plastic Material
        bsdf.inputs['Base Color'].default_value = (random.random(), random.random(), random.random(), 1)  # Random plastic color
        bsdf.inputs['Metallic'].default_value = 0  # Non-metallic
        bsdf.inputs['Roughness'].default_value = 0.4  # Slightly rough plastic finish
    
    elif material_type == 'Wood':
        # Wood Material
        bsdf.inputs['Base Color'].default_value = (0.6, 0.3, 0.1, 1)  # Wood-like color
        bsdf.inputs['Metallic'].default_value = 0  # Non-metallic
        bsdf.inputs['Roughness'].default_value = 0.7  # Rough texture for wood
    
    elif material_type == 'Glass':
        # Glass Material
        bsdf.inputs['Base Color'].default_value = (1, 1, 1, 0.1)  # Transparent color (white with low alpha)
        bsdf.inputs['Metallic'].default_value = 0  # Non-metallic
        bsdf.inputs['Roughness'].default_value = 0.05  # Low roughness for glass
        if "Transmission" in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 1  # Full transparency (glass effect)
    
    elif material_type == 'Stone':
        # Stone Material
        bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1)  # Gray stone color
        bsdf.inputs['Metallic'].default_value = 0  # Non-metallic
        bsdf.inputs['Roughness'].default_value = 0.8  # High roughness for stone

    return mat

# Function to add random complex shapes on the floor
def add_complex_random_objects_on_floor(num_objects, min_x, max_x, min_y, max_y, max_size=2.0):
    for _ in range(num_objects):
        # Randomly choose the object type (complex shapes)
        object_type = random.choice(['TORUS_KNOT', 'TWISTED_CYLINDER', 'ICOSPHERE', 'SUBDIVIDED_CUBE', 
                                     'BOOLEAN_OBJECT', 'CONE', 'TORUS', 'MONKEY', 'UV_SPHERE'])
        
        # Create the object based on the type
        if object_type == 'TORUS_KNOT':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_torus_add(major_radius=2, minor_radius=0.3, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Torus Knot"

        elif object_type == 'TWISTED_CYLINDER':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Twisted Cylinder"
            obj.rotation_euler.x = math.radians(90)  # Rotate to make it stand upright
            # Add twist modifier
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            obj.modifiers["SimpleDeform"].deform_method = 'TWIST'
            obj.modifiers["SimpleDeform"].angle = math.radians(90)  # Twist by 90 degrees

        elif object_type == 'ICOSPHERE':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Icosphere"
        
        elif object_type == 'SUBDIVIDED_CUBE':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Subdivided Cube"
            # Add subdivision surface modifier
            bpy.ops.object.modifier_add(type='SUBSURF')
            obj.modifiers["Subdivision"].levels = 2  # Add 2 levels of subdivision

        elif object_type == 'BOOLEAN_OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Boolean Object"
            
            # Add a sphere and use boolean modifier to subtract it from the cube
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
            sphere = bpy.context.object
            sphere.name = "Sphere"
            
            # Add Boolean modifier to the cube and subtract the sphere
            boolean_mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
            boolean_mod.operation = 'DIFFERENCE'
            boolean_mod.use_self = True
            boolean_mod.object = sphere
            
            # Apply the boolean modifier
            bpy.context.view_layer.objects.active = obj  # Make the cube the active object
            bpy.ops.object.modifier_apply(modifier=boolean_mod.name)
            bpy.data.objects.remove(sphere)  # Remove the sphere after operation

        elif object_type == 'CONE':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=1, depth=2, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Cone"
            obj.rotation_euler.x = math.radians(90)  # Align cone to lie on the floor

        elif object_type == 'TORUS':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_torus_add(major_radius=2, minor_radius=0.4, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Torus"
            obj.rotation_euler.x = math.radians(90)  # Align torus to lie flat on the floor

        elif object_type == 'MONKEY':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "Suzanne"

        elif object_type == 'UV_SPHERE':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
            obj = bpy.context.object
            obj.name = "UV Sphere"

        # Randomize position within specified bounds on the X and Y axes (floor level at Z=0)
        obj.location.x = random.uniform(min_x, max_x)
        obj.location.y = random.uniform(min_y, max_y)

        # Correct the Z-axis position to place the object correctly on the floor
        # Compute the object's bounding box size
        obj_dim = obj.dimensions.z
        obj.location.z = obj_dim / 2  # Position it so the bottom is at Z=0

        # Randomize rotation (Euler angles)
        obj.rotation_euler.x = random.uniform(0, math.pi)
        obj.rotation_euler.y = random.uniform(0, math.pi)
        obj.rotation_euler.z = random.uniform(0, math.pi)

        # Optionally, randomize the scale of the object within a maximum size limit
        scale_factor = random.uniform(0.5, max_size)  # Random scale factor up to max_size
        obj.scale = (scale_factor, scale_factor, scale_factor)

        # Add a realistic material to the object
        material = create_realistic_material()
        obj.data.materials.append(material)

add_complex_random_objects_on_floor(10, -7, 7, -7, 7, max_size=0.9)




####### HOVERING DRONE #########

# Import the drone FBX file
fbx_file_path = "drone.fbx"  # Update this path to your actual FBX file location
bpy.ops.import_scene.fbx(filepath=fbx_file_path)

# Get all imported objects
if bpy.context.selected_objects:
    drone_parts = bpy.context.selected_objects[:]  # This stores the list of imported drone parts
else:
    raise Exception("No objects selected after import. Check your FBX file.")

# Scale down the imported drone parts
scale_factor = 0.001  # Adjust this value as needed (e.g., 0.5 for half size)
for part in drone_parts:
    part.scale = (scale_factor, scale_factor, scale_factor)

# Create an empty object to serve as the parent for all drone parts
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0), rotation=(0, 0, 0))
hovering_drone = bpy.context.active_object

hovering_drone.location = (0, 0, 3)
hovering_drone.rotation_euler = (math.radians(90), 0, 0)

# Parent all the drone parts to the empty object
for part in drone_parts:
    part.select_set(True)  # Select each drone part
    part.parent = hovering_drone  # Set the parent

# Add camera to hovering drone
bpy.ops.object.camera_add(location=(0.07, 0.1, 0.1), rotation=(math.radians(-90), math.radians(-90), 0))
camera = bpy.context.active_object
camera.parent = hovering_drone
camera.name = 'Drone Camera'

# Set camera as active
bpy.context.scene.camera = camera

# Adjust camera settings for a larger field of view (wider view)
camera.data.lens = 18  # Decrease the focal length (default is 50) for a wider field of view
camera.data.sensor_width = 100  # Standard full-frame sensor width (you can increase this for even wider FOV)

# Optional: If you want to increase the camera's clipping distance (to see more objects in the scene)
camera.data.clip_start = 0.1  # Set the start clipping distance to a smaller value
camera.data.clip_end = frames_per_folder  # Set the end clipping distance to a larger value



####### FLYING DRONE #########

# Create flying drone
#bpy.ops.mesh.primitive_cube_add(size=0.3)

# Import the drone FBX file
fbx_file_path = "drone.fbx"  # Update this path to your actual FBX file location
bpy.ops.import_scene.fbx(filepath=fbx_file_path)

# Get all imported objects
if bpy.context.selected_objects:
    drone_parts = bpy.context.selected_objects[:]  # This stores the list of imported drone parts
else:
    raise Exception("No objects selected after import. Check your FBX file.")
    
# Scale down the imported drone parts
scale_factor = 0.001  # Adjust this value as needed (e.g., 0.5 for half size)
for part in drone_parts:
    part.scale = (scale_factor, scale_factor, scale_factor)


# Create an empty object to serve as the parent for all drone parts
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0), rotation=(0, 0, 0))
flying_drone = bpy.context.active_object

# Adjust the position and rotation of the flying drone (parent object)
flying_drone.location = (0, 0, 3)
flying_drone.rotation_euler = (math.radians(90), 0, 0)

# Parent all the drone parts to the empty object (flying_drone)
for part in drone_parts:
    part.select_set(True)  # Select each drone part
    part.parent = flying_drone  # Set the parent
    part.select_set(False)  # Deselect after setting the parent

## Add camera to hovering drone
#bpy.ops.object.camera_add(location=(0.07, 0.1, 0.1), rotation=(math.radians(-90), math.radians(-90), 0))
#hovering_camera = bpy.context.active_object
#hovering_camera.name = 'Hovering Drone Camera'

# Now move the flying_drone empty to a higher position
flying_drone.location = (0, 0, 6)  # Start above the hovering drone

# Add camera to flying drone (facing downward)
bpy.ops.object.camera_add(location=(0.07, 0.1, 0.1), rotation=(math.pi, 0, 0))
secondary_camera = bpy.context.active_object
secondary_camera.name = 'Flying Drone Camera'

# Parent the secondary camera to the flying drone
secondary_camera.parent = flying_drone

# Make sure the primary camera is parented correctly to the drone structure
#hovering_camera.parent = flying_drone  # Parent the hovering camera to the flying drone



def add_carpet():
    # Create a plane for the carpet
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0.1))  # Create a plane just above the floor
    carpet = bpy.context.active_object
    carpet.name = "Carpet"
    
    # Scale the carpet to match the room's floor size
    carpet.scale = (14, 14, 1)  # Adjust size to match the room floor size
    
    # Create a new material for the carpet
    mat = bpy.data.materials.new(name="CarpetMaterial")
    mat.use_nodes = True  # Enable nodes for material
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    # Randomly decide whether to create a realistic or plain carpet
    # if random.choice([True, False]):  # Randomly choose between realistic or plain carpet
    if False:
        # Create a realistic carpet with texture
        print("Creating realistic carpet")

        # Create a procedural pattern for the carpet using Noise Texture
        noise_texture = mat.node_tree.nodes.new(type="ShaderNodeTexNoise")
        noise_texture.location = (-400, 0)
        noise_texture.inputs["Scale"].default_value = random.uniform(5, 15)  # Random scale for randomness
        noise_texture.inputs["Detail"].default_value = random.uniform(2, 10)  # Add detail for carpet fibers
        
        # Optionally, use a Voronoi Texture for a different pattern
        voronoi_texture = mat.node_tree.nodes.new(type="ShaderNodeTexVoronoi")
        voronoi_texture.location = (-600, 0)
        voronoi_texture.inputs["Scale"].default_value = random.uniform(10, 30)  # Random scale for Voronoi pattern
        
        # Mix the noise and Voronoi textures to get a more varied pattern
        mix_shader = mat.node_tree.nodes.new(type="ShaderNodeMixRGB")
        mix_shader.location = (-200, 0)
        mix_shader.inputs["Fac"].default_value = random.random()  # Randomize the blending between noise and Voronoi
        mat.node_tree.links.new(mix_shader.inputs[1], noise_texture.outputs["Color"])
        mat.node_tree.links.new(mix_shader.inputs[2], voronoi_texture.outputs["Color"])
        
        # Set base color for the realistic carpet (random color range for variation)
        base_color = (random.uniform(0.3, 0.5), random.uniform(0.1, 0.3), random.uniform(0.0, 0.2), 1)  # Limited color range
        mat.node_tree.links.new(bsdf.inputs["Base Color"], mix_shader.outputs["Color"])

        # Set roughness to give a carpet-like surface (higher roughness for a matte look)
        bsdf.inputs["Roughness"].default_value = random.uniform(0.6, 0.9)  # Higher roughness for a non-glossy, matte appearance
        
        # Add bump mapping to simulate carpet fibers (using Noise Texture)
        bump_node = mat.node_tree.nodes.new(type="ShaderNodeBump")
        bump_node.location = (-400, -200)
        bump_node.inputs["Strength"].default_value = random.uniform(0.1, 0.3)  # Random bump strength
        
        # Use the noise texture for bump mapping
        mat.node_tree.links.new(bump_node.inputs["Height"], noise_texture.outputs["Color"])
        
        # Connect the bump node to the material's normal input
        mat.node_tree.links.new(bsdf.inputs["Normal"], bump_node.outputs["Normal"])
    
    else:
        # Create a plain carpet (solid color)
        print("Creating plain carpet")

        # Set base color for plain carpet (solid color)
        base_color = (random.uniform(0.3, 0.5), random.uniform(0.1, 0.3), random.uniform(0.0, 0.2), 1)  # Solid color
        bsdf.inputs["Base Color"].default_value = base_color

        # Set roughness to give a carpet-like surface (higher roughness for a matte look)
        bsdf.inputs["Roughness"].default_value = random.uniform(0.7, 0.9)  # Higher roughness for a matte finish
    
    # Assign the material to the carpet
    if carpet.data.materials:
        carpet.data.materials[0] = mat
    else:
        carpet.data.materials.append(mat)

# Add the carpet (either plain or realistic)
add_carpet()


# Function to add a random light at a location within specified min/max X, Y, Z limits
def add_random_light(min_x, max_x, min_y, max_y, min_z, max_z):
    # Randomly select a location within the provided bounds for X, Y, and Z
    location = (random.uniform(min_x, max_x), 
                random.uniform(min_y, max_y), 
                random.uniform(min_z, max_z))  
    light_data = bpy.data.lights.new(name="Light", type='AREA')
    light_data.energy = random.uniform(50, 150)  # Random energy range
    light_object = bpy.data.objects.new(name="Light", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = location

# Function to add multiple random lights
def add_multiple_random_lights(num_lights, min_x, max_x, min_y, max_y, min_z, max_z):
    for _ in range(num_lights):
        add_random_light(min_x, max_x, min_y, max_y, min_z, max_z)

# Example: Add x random lights within the bounds of min_x, max_x, min_y, max_y, min_z, max_z
add_multiple_random_lights(10, -10, 10, -10, 10, 10, 15)


# Animation settings
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = frames_per_folder  # Increased frame count for longer animation

def generate_random_point():
    x = random.uniform(-8, 8)
    y = random.uniform(-8, 8)
    z = random.uniform(3, 5)
    return Vector((x, y, z))

def animate_flying_drone():
    current_point = Vector(flying_drone.location)
    
    for frame in range(scene.frame_start, scene.frame_end + 1, 20):
        next_point = generate_random_point()
        direction = (next_point - current_point).normalized()
        
        # Calculate rotation to face the direction of movement while keeping camera down
        rotation = Euler((math.pi / 2 , 0 , math.atan2(direction.y, direction.x)))
        
        # Interpolate between current_point and next_point
        for i in range(20):
            t = i / 20
            interpolated_point = current_point.lerp(next_point, t)
            
            flying_drone.location = interpolated_point
            flying_drone.rotation_euler = rotation
            flying_drone.keyframe_insert(data_path="location", frame=frame + i)
            flying_drone.keyframe_insert(data_path="rotation_euler", frame=frame + i)
        
        current_point = next_point
    
    # Set interpolation to smooth the movement
    if flying_drone.animation_data and flying_drone.animation_data.action:
        for fc in flying_drone.animation_data.action.fcurves:
            for kf in fc.keyframe_points:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = 'AUTO'
                kf.handle_right_type = 'AUTO'


print("Starting animation...")
animate_flying_drone()
print("Animation complete.")

# Define the base output directory
base_output_dir = bpy.path.abspath("nlos_dataset/")

# Function to save the image and JSON file
def save_image_and_json(frame, folder_name, frame_within_batch, drone_1_pose, drone_2_pose):
    # File paths
    image_file_name = f"seq_{folder_name}_{frame_within_batch:04d}.exr"
    json_file_name = f"seq_{folder_name}_{frame_within_batch:04d}.json"
    
    # Output directory for the current batch
    output_dir = os.path.join(base_output_dir, f"seq_{folder_name:04d}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Set image filepath
    bpy.context.scene.render.filepath = os.path.join(output_dir, image_file_name)
    
    # Render the image
    bpy.ops.render.render(write_still=True)
    print(f"Rendered image: {bpy.context.scene.render.filepath}")
    
    
    json_data = {
        "timestamp": frame,
        "drone_1_pose": {
            "position": {"x": drone_1_pose.location.x, "y": drone_1_pose.location.y, "z": drone_1_pose.location.z},
            "orientation": {
                "roll": drone_1_pose.rotation_euler.x,
                "pitch": drone_1_pose.rotation_euler.y,
                "yaw": drone_1_pose.rotation_euler.z
            }
        },
        "drone_2_pose": {
            "position": {"x": drone_2_pose.location.x, "y": drone_2_pose.location.y, "z": drone_2_pose.location.z},
            "orientation": {
                "roll": drone_2_pose.rotation_euler.x,
                "pitch": drone_2_pose.rotation_euler.y,
                "yaw": drone_2_pose.rotation_euler.z
            }
        },
        "image_path": bpy.context.scene.render.filepath
    }

    # Save JSON file
    json_file_path = os.path.join(output_dir, json_file_name)
    with open(json_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Saved JSON: {json_file_path}")


# Set up NLOS simulation 
def setup_nlos_simulation():
    # Add a plane to represent the NLOS surface
    bpy.ops.mesh.primitive_plane_add(size=18, location=(0, 0, 0))
    nlos_surface = bpy.context.active_object
    nlos_surface.name = 'NLOS Surface'
    
    # Add a material to the NLOS surface
    mat = bpy.data.materials.new(name="NLOS Material")
    mat.use_nodes = True
    nlos_surface.data.materials.append(mat)
    
    # Set up nodes for NLOS effect (simplified)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add Principled BSDF node
    node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_principled.inputs['Roughness'].default_value = 1.0
    
    # Add Emission node for glow effect
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_emission.inputs['Strength'].default_value = 0.5
    
    # Add Mix Shader node
    node_mix = nodes.new(type='ShaderNodeMixShader')
    node_mix.inputs[0].default_value = 0.2
    
    # Add Material Output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    links.new(node_principled.outputs['BSDF'], node_mix.inputs[1])
    links.new(node_emission.outputs['Emission'], node_mix.inputs[2])
    links.new(node_mix.outputs['Shader'], node_output.inputs['Surface'])

# Set up NLOS simulation
setup_nlos_simulation()

# Set render engine to Cycles for better lighting simulation
bpy.context.scene.render.engine = 'CYCLES'

# Set up render settings
bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
bpy.context.scene.render.image_settings.color_mode = 'RGBA' 
bpy.context.scene.render.filepath = "nlos_dataset/"

# Ensure the output directory exists
output_dir = bpy.path.abspath(bpy.context.scene.render.filepath)
os.makedirs(output_dir, exist_ok=True)

# Set the hovering drone's camera as the active camera
bpy.context.scene.camera = camera

# Render settings to preserve NLOS signals
bpy.context.scene.cycles.use_denoising = False  # Disable denoising to preserve NLOS signals


# Function to render images and save corresponding JSON files
def render_images_and_json():
    for frame in range(scene.frame_start, scene.frame_end + 1):
        # Determine the folder number (batch number)
        folder_number = (frame - 1) // frames_per_folder + starting_folder_number
        frame_within_batch = (frame - 1) % frames_per_folder + 1  # Frame number within the current batch

        bpy.context.scene.frame_set(frame)
        bpy.ops.render.render(write_still=True)

        # Get the poses of both drones (hovering_drone and flying_drone)
        drone_1_pose = hovering_drone
        drone_2_pose = flying_drone
        
        # Save image and corresponding JSON file
        save_image_and_json(frame, folder_number, frame_within_batch, drone_1_pose, drone_2_pose)


# Start rendering the frames and saving JSON data
render_images_and_json()

print(f"Rendering complete. Images saved in {output_dir}")

# Exit Blender after rendering (for headless operation)
bpy.ops.wm.quit_blender()