import pkgutil
import inspect
import csv
import manim
from manim import Mobject, Animation, Scene

def collect_subclasses(package, base_class):
    results = []
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = __import__(module_name, fromlist=["dummy"])
        except Exception:
            continue  # skip modules that fail to import
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, base_class) and cls is not base_class:
                doc = (inspect.getdoc(cls) or "").replace("\n", " ").strip()
                results.append((name, cls.__module__, inspect.getfile(cls), doc))
    return sorted(results, key=lambda x: (x[1], x[0]))

def export_to_csv(filename, category, results):
    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([category])  # Section header
        writer.writerow(["Class Name", "Module", "File Path", "Description"])  # Headers
        for name, module, filepath, doc in results:
            writer.writerow([name, module, filepath, doc])
        writer.writerow([])  # Blank line between categories

# Collect subclasses
mobjects = collect_subclasses(manim.mobject, Mobject)
animations = collect_subclasses(manim.animation, Animation)
scenes = collect_subclasses(manim.scene, Scene)

# Export everything
filename = "manim_classes_with_description.csv"
with open(filename, "w", newline="", encoding="utf-8") as f:
    pass  # clear file first

export_to_csv(filename, "Mobjects", mobjects)
export_to_csv(filename, "Animations", animations)
export_to_csv(filename, "Scenes", scenes)

print(f"✅ Exported Class Name, Module, File Path, and Description to {filename}")
