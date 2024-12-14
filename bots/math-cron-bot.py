import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from io import BytesIO
from sympy import symbols
from atproto import Client, models
from apscheduler.events import EVENT_JOB_EXECUTED

# Load environment variables
load_dotenv()

# Bluesky credentials (example usage if needed)
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

class MathProblemGenerator:
    def __init__(self):
        self.problem_generators = [self.generate_complex_number_problem]

    def generate_complex_number_problem(self):
        operation = random.choice(["+", "-"])
        a_real, a_imag = random.randint(1, 10), random.randint(1, 10)
        b_real, b_imag = random.randint(1, 10), random.randint(1, 10)

        a = complex(a_real, a_imag)
        b = complex(b_real, b_imag)

        problem = f"({a_real} + {a_imag}i) {operation} ({b_real} + {b_imag}i) = ?"
        solution = a + b if operation == "+" else a - b
        return problem, f"{solution.real} + {solution.imag}i"

    def generate_problems(self, count=5):
        problems = []
        for _ in range(count):
            generator = random.choice(self.problem_generators)
            problem, solution = generator()
            problems.append((problem, solution))
        return problems

    def render_to_png(self, problems, output_path="math_problems.png"):
        fig, ax = plt.subplots(figsize=(6, len(problems) * 1))
        ax.axis("off")

        content = "\n".join([f"{i + 1}. {prob}" for i, (prob, _) in enumerate(problems)])
        ax.text(0.5, 0.5, content, fontsize=12, va="center", ha="center", wrap=True)

        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

    def save_solutions(self, problems, output_path="solutions.txt"):
        with open(output_path, "w") as f:
            for i, (_, solution) in enumerate(problems):
                f.write(f"{i + 1}. {solution}\n")

# Function to periodically generate and post problems
def generate_and_post_math_problems():
    generator = MathProblemGenerator()
    problems = generator.generate_problems(count=5)
    output_path = "math_problems.png"
    solutions_path = "solutions.txt"

    generator.render_to_png(problems, output_path=output_path)
    generator.save_solutions(problems, output_path=solutions_path)

    # Post to Bluesky
    client = Client("https://bsky.social")
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)

    # Post the problems first
    with open(output_path, 'rb') as f:
        img_data = f.read()

    aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(height=100, width=100)

    problem_post = client.send_image(
        text='Here are some math problems for you!',
        image=img_data,
        image_alt='Math problems and their solutions',
        image_aspect_ratio=aspect_ratio,
    )

    # Post the solutions as a reply
    with open(solutions_path, "r") as f:
        solutions_text = f.read()

    root_post_ref = models.create_strong_ref(problem_post)

    # Reply to the root post. We need to pass ReplyRef with root and parent
    reply_to_root = models.create_strong_ref(
        client.send_post(
            text=f"Here are the solutions:\n\n{solutions_text}",
            reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref),
        )
    )

def job_listener(event):
    if event.code == EVENT_JOB_EXECUTED:
        print(f"Job {event.job_id} executed at {event.scheduled_run_time}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Generate and render problems every hour
    scheduler.add_job(generate_and_post_math_problems, "cron", hour="23")
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED)
    scheduler.start()
