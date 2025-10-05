from manim import *
from random import uniform
import numpy as np

config.renderer = "opengl"

class ProperBouncingBalls(ThreeDScene):
    def construct(self):
        SPHERE_RADIUS = 4.0
        BALL_RADIUS = 0.2
        NUM_BALLS = 3
        DAMPING = 0.82
        GRAVITY = np.array([0, 0, -0.5])
        ROTATION_RATE = 0.25  

        class BouncingBall:
            def __init__(self):
                self.position = np.array([
                    uniform(-SPHERE_RADIUS*0.9, SPHERE_RADIUS*0.9),
                    uniform(-SPHERE_RADIUS*0.9, SPHERE_RADIUS*0.9),
                    uniform(-SPHERE_RADIUS*0.9, SPHERE_RADIUS*0.9)
                ])
                self.velocity = np.array([
                    uniform(-2, 2),
                    uniform(-2, 2),
                    uniform(-2, 2)
                ])
                self.mesh = Sphere(radius=BALL_RADIUS, resolution=(15,15))
                self.mesh.set_color(YELLOW)
                self.mesh.set_opacity(0.9)
                self.mesh.add_updater(lambda m: m.move_to(self.position))

        container = Sphere(
            radius=SPHERE_RADIUS,
            color=BLUE_B,
            resolution=(30,30)
        )
        container.set_opacity(0.07)
        container.set_stroke(width=1, opacity=0.3) 

        edge_glow = Surface(
            lambda u, v: np.array([
                (SPHERE_RADIUS*1.01) * np.cos(u) * np.cos(v),
                (SPHERE_RADIUS*1.01) * np.sin(u) * np.cos(v),
                (SPHERE_RADIUS*1.01) * np.sin(v)
            ]),
            u_range=[0, 2*PI],
            v_range=[-PI/2, PI/2],
            color=BLUE_D,
            resolution=(30,30)
        )
        edge_glow.set_opacity(0.15)
        edge_glow.set_fill(color=BLUE_D, opacity=0.15)  
        particles = [BouncingBall() for _ in range(NUM_BALLS)]

        rotation_tracker = ValueTracker(0)

        def update_physics(dt):
            for p in particles:
                p.velocity += GRAVITY * dt

                p.position += p.velocity * dt

                distance = np.linalg.norm(p.position)
                if distance >= SPHERE_RADIUS - BALL_RADIUS:
                    normal = p.position / distance
                    p.position = normal * (SPHERE_RADIUS - BALL_RADIUS)
               
                    tangent_vel = p.velocity - np.dot(p.velocity, normal) * normal
                    normal_vel = np.dot(p.velocity, normal) * normal
                    p.velocity = tangent_vel - DAMPING * normal_vel


        def rotate_container(mob, dt):
            angle = rotation_tracker.get_value() + ROTATION_RATE * DEGREES
            rotation_tracker.set_value(angle)
            mob.rotate(ROTATION_RATE * DEGREES, axis=UP, about_point=ORIGIN)

        self.set_camera_orientation(phi=60*DEGREES, theta=45*DEGREES, distance=10)
        self.add(container, edge_glow)
        for p in particles:
            self.add(p.mesh)

        container.add_updater(rotate_container)
        edge_glow.add_updater(rotate_container)

        physics_updater = VGroup()
        physics_updater.add_updater(lambda m, dt: update_physics(dt))
        self.add(physics_updater)

        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(20)
        self.stop_ambient_camera_rotation()

if __name__ == "__main__":
    scene = ProperBouncingBalls()
    scene.render()
