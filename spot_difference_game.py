import tkinter as tk
from tkinter import filedialog, messagebox
import random
import platform
import sys

try:
    from PIL import Image, ImageTk
    import cv2
    import numpy as np
except ImportError as error:
    print(f"Missing required package: {error.name}")
    print("Install the project requirements with:")
    print("python3 -m pip install -r requirements.txt")
    sys.exit(1)


DIFFERENCE_COUNT = 5
CANVAS_SIZE = 500


def tkinter_can_start():
    return not (
        platform.system() == "Darwin" and
        getattr(tk, "TkVersion", 0) < 8.6
    )


class Difference:
    def __init__(self, x, y, radius, diff_type):
        self.x = x
        self.y = y
        self.radius = radius
        self.diff_type = diff_type
        self.found = False


class ImageProcessor:
    def __init__(self):
        self.differences = []

    def resize_keep_ratio(self, image, max_width=CANVAS_SIZE, max_height=CANVAS_SIZE):
        h, w = image.shape[:2]

        scale = min(max_width / w, max_height / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(image, (new_w, new_h))

        return resized

    def is_overlapping(self, x, y, radius):
        for diff in self.differences:
            distance = np.sqrt((x - diff.x) ** 2 + (y - diff.y) ** 2)

            if distance < radius + diff.radius + 40:
                return True

        return False

    def generate_differences(self, image):
        modified = image.copy()

        self.differences = []

        h, w = modified.shape[:2]

        if w < 120 or h < 120:
            raise ValueError("Please choose an image that is at least 120 x 120 pixels.")

        difference_types = [
            "color_change",
            "missing_object",
            "blur_region"
        ]

        attempts = 0
        max_attempts = 500

        while len(self.differences) < DIFFERENCE_COUNT and attempts < max_attempts:

            attempts += 1

            radius = random.randint(20, 35)

            x = random.randint(radius + 20, w - radius - 20)
            y = random.randint(radius + 20, h - radius - 20)

            if self.is_overlapping(x, y, radius):
                continue

            diff_type = random.choice(difference_types)

            if diff_type == "color_change":

                overlay = modified.copy()

                color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )

                cv2.circle(overlay, (x, y), radius, color, -1)

                alpha = 0.6

                modified = cv2.addWeighted(
                    overlay,
                    alpha,
                    modified,
                    1 - alpha,
                    0
                )

            elif diff_type == "missing_object":

                cv2.rectangle(
                    modified,
                    (x - radius, y - radius),
                    (x + radius, y + radius),
                    (255, 255, 255),
                    -1
                )

            elif diff_type == "blur_region":

                x1 = max(0, x - radius)
                y1 = max(0, y - radius)

                x2 = min(w, x + radius)
                y2 = min(h, y + radius)

                region = modified[y1:y2, x1:x2]

                blurred = cv2.GaussianBlur(region, (21, 21), 0)

                modified[y1:y2, x1:x2] = blurred

            self.differences.append(
                Difference(x, y, radius, diff_type)
            )

        if len(self.differences) < DIFFERENCE_COUNT:
            raise ValueError(
                "Could not place enough differences. Please choose a larger or less narrow image."
            )

        return modified


class SpotDifferenceGame:

    def __init__(self, root):

        self.root = root

        self.root.title("Spot The Difference Game")

        self.root.geometry("1200x700")

        self.processor = ImageProcessor()

        self.original_image = None
        self.modified_image = None

        self.original_tk = None
        self.modified_tk = None

        self.score = 0
        self.mistakes = 0

        self.max_mistakes = 3

        self.game_over = False

        self.setup_ui()

    def setup_ui(self):

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.load_button = tk.Button(
            top_frame,
            text="Load Image",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=8,
            command=self.load_image
        )

        self.load_button.grid(row=0, column=0, padx=10)

        self.reveal_button = tk.Button(
            top_frame,
            text="Reveal Remaining",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=8,
            command=self.reveal_remaining
        )

        self.reveal_button.grid(row=0, column=1, padx=10)

        self.reset_button = tk.Button(
            top_frame,
            text="Reset Game",
            font=("Arial", 14, "bold"),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=8,
            command=self.reset_game
        )

        self.reset_button.grid(row=0, column=2, padx=10)

        self.info_label = tk.Label(
            self.root,
            text="Load an image to start the game",
            font=("Arial", 16, "bold")
        )

        self.info_label.pack(pady=10)

        image_frame = tk.Frame(self.root)
        image_frame.pack()

        left_frame = tk.Frame(image_frame)
        left_frame.grid(row=0, column=0, padx=15)

        right_frame = tk.Frame(image_frame)
        right_frame.grid(row=0, column=1, padx=15)

        tk.Label(
            left_frame,
            text="Original Image",
            font=("Arial", 14, "bold")
        ).pack()

        tk.Label(
            right_frame,
            text="Modified Image",
            font=("Arial", 14, "bold")
        ).pack()

        self.original_canvas = tk.Canvas(
            left_frame,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="lightgray"
        )

        self.original_canvas.pack()

        self.modified_canvas = tk.Canvas(
            right_frame,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="lightgray"
        )

        self.modified_canvas.pack()

        self.original_canvas.bind(
            "<Button-1>",
            self.check_click
        )

        self.modified_canvas.bind(
            "<Button-1>",
            self.check_click
        )

    def load_image(self):

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp")
            ]
        )

        if not file_path:
            return

        image = cv2.imread(file_path)

        if image is None:
            messagebox.showerror(
                "Error",
                "Could not load image"
            )
            return

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        image = self.processor.resize_keep_ratio(image)

        self.original_image = image.copy()

        try:
            self.modified_image = self.processor.generate_differences(image)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            self.original_image = None
            self.modified_image = None
            return

        self.score = 0
        self.mistakes = 0

        self.game_over = False

        self.update_status()

        self.display_images()

    def display_images(self):

        original_display = self.original_image.copy()

        modified_display = self.modified_image.copy()

        for diff in self.processor.differences:

            if diff.found:

                cv2.circle(
                    original_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (255, 0, 0),
                    3
                )

                cv2.circle(
                    modified_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (255, 0, 0),
                    3
                )

        self.show_image(
            original_display,
            self.original_canvas,
            "original"
        )

        self.show_image(
            modified_display,
            self.modified_canvas,
            "modified"
        )

    def show_image(self, image, canvas, side):

        h, w = image.shape[:2]

        pil_image = Image.fromarray(image)

        tk_image = ImageTk.PhotoImage(pil_image)

        canvas.delete("all")

        x = (CANVAS_SIZE - w) // 2
        y = (CANVAS_SIZE - h) // 2

        canvas.create_image(
            x,
            y,
            anchor=tk.NW,
            image=tk_image
        )

        if side == "original":
            self.original_tk = tk_image
        else:
            self.modified_tk = tk_image

    def check_click(self, event):

        if self.game_over:
            return

        if self.original_image is None:
            return

        img_h, img_w = self.original_image.shape[:2]

        offset_x = (CANVAS_SIZE - img_w) // 2
        offset_y = (CANVAS_SIZE - img_h) // 2

        click_x = event.x - offset_x
        click_y = event.y - offset_y

        correct_click = False

        for diff in self.processor.differences:

            if diff.found:
                continue

            distance = np.sqrt(
                (click_x - diff.x) ** 2 +
                (click_y - diff.y) ** 2
            )

            if distance <= diff.radius + 15:

                diff.found = True

                self.score += 1

                correct_click = True

                break

        if not correct_click:

            self.mistakes += 1

            if self.mistakes >= self.max_mistakes:

                self.game_over = True

                messagebox.showwarning(
                    "Game Over",
                    "You reached 3 mistakes"
                )

        if self.score == DIFFERENCE_COUNT:

            self.game_over = True

            messagebox.showinfo(
                "Congratulations",
                f"You found all {DIFFERENCE_COUNT} differences!"
            )

        self.update_status()

        self.display_images()

    def reveal_remaining(self):

        if self.original_image is None:
            return

        original_display = self.original_image.copy()

        modified_display = self.modified_image.copy()

        for diff in self.processor.differences:

            if not diff.found:

                cv2.circle(
                    original_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (0, 0, 255),
                    4
                )

                cv2.circle(
                    modified_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (0, 0, 255),
                    4
                )

                diff.found = True

        self.score = DIFFERENCE_COUNT

        self.game_over = True

        self.update_status()

        self.show_image(
            original_display,
            self.original_canvas,
            "original"
        )

        self.show_image(
            modified_display,
            self.modified_canvas,
            "modified"
        )

    def reset_game(self):

        if self.original_image is None:
            return

        try:
            self.modified_image = self.processor.generate_differences(
                self.original_image
            )
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        self.score = 0
        self.mistakes = 0

        self.game_over = False

        self.update_status()

        self.display_images()

    def update_status(self):

        remaining = DIFFERENCE_COUNT - self.score

        self.info_label.config(
            text=
            f"Score: {self.score}/{DIFFERENCE_COUNT}    "
            f"Remaining: {remaining}    "
            f"Mistakes: {self.mistakes}/3"
        )


if __name__ == "__main__":

    if not tkinter_can_start():
        print("Could not start the Tkinter window.")
        print(f"This Python is using Tk {tk.TkVersion}, which is too old for this macOS setup.")
        print()
        print("Install and run the file with a Python that includes Tk 8.6 or newer.")
        print("Good options on macOS are the official Python installer from python.org")
        print("or Homebrew Python.")
        sys.exit(1)

    try:
        root = tk.Tk()
    except tk.TclError as error:
        print("Could not start the Tkinter window.")
        print(error)
        print()
        print("On macOS, try running this with a Python install that includes a working Tk,")
        print("such as the official Python installer from python.org or Homebrew Python.")
        sys.exit(1)

    game = SpotDifferenceGame(root)

    root.mainloop()
