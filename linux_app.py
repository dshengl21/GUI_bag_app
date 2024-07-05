import tkinter as tk
from tkinter import ttk
import subprocess


def run_command(command, display_label):
    try:
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            display_label.config(text="Success\n" + result.stdout, fg="green")
        else:
            display_label.config(text="Error\n" + result.stderr, fg="red")
    except subprocess.CalledProcessError as e:
        display_label.config(text="Execution Failed\n" + str(e), fg="red")
    except Exception as e:
        display_label.config(text="Error\n" + str(e), fg="red")

def reset_tab(tab_name):
    global YEAR, MONTH, DAY, DATE, BAG_PATH, START_TIME, DURATION
    if tab_name == "check":
        # Reset logic for the Check tab
        lbl_space.config(text="")
        lbl_space_message.config(text="rpool free storage should be > 500GB. If not, click Remove Bags")
        lbl_remove_bags.config(text="")
        lbl_cluster1.config(text="")
        lbl_cluster2.config(text="")
        lbl_cluster_login.config(text="")
    elif tab_name == "bag":
        # Reset logic for the Bag tab
        list_bags_output.config(text="")
        copy_bag_output.config(text="")
        check_bag_output.config(text="")
        estimate_times_output_label.config(text="")
        extract_videos_output.config(text="")
        year_entry.delete(0, tk.END)
        month_entry.delete(0, tk.END)
        day_entry.delete(0, tk.END)
        start_time_entry.delete(0, tk.END)
        duration_entry.delete(0, tk.END)
        YEAR = MONTH = DAY = DATE = BAG_PATH = START_TIME = DURATION = None


def add_reset_button(tab, tab_name):
    reset_btn_frame = ttk.Frame(tab)
    reset_btn_frame.pack(side="top", anchor="ne")

    reset_btn = ttk.Button(reset_btn_frame, text="↻", command=lambda: reset_tab(tab_name))
    reset_btn.pack()


def check_space(lbl_space, lbl_space_message):
    lbl_space_message.config(text="rpool free storage should be > 500GB. If not, click Remove Bags")
    run_command("zpool list", lbl_space)

def create_button_with_label(parent, text, command):
    frame = ttk.Frame(parent)
    button = ttk.Button(parent, text=text, command=command)
    label = tk.Label(frame)
    
    button.pack(side="top")
    label.pack(side="top", fill="both")
    frame.pack(fill="x", pady=10, padx=367, anchor='center')

    return label


    


def add_scrollable_frame(tab):
    '''Create a scrollable frame in the given tab with both vertical and horizontal scrollbars'''
    canvas = tk.Canvas(tab)
    v_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    h_scrollbar = ttk.Scrollbar(tab, orient="horizontal", command=canvas.xview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((374, 0), window=scrollable_frame, anchor="n")
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    canvas.pack(side="top", fill="both", expand=True)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")


    return scrollable_frame


        

    
# Setup GUI
root = tk.Tk()
root.title("Bags Download Application")

# Set the initial size of the window (width x height)
root.geometry("800x550")  # adjust as needed



tab_control = ttk.Notebook(root)
tab_check = ttk.Frame(tab_control)
tab_bag = ttk.Frame(tab_control)

# Adding Scrollable Frames to Tabs
scrollable_frame_check = add_scrollable_frame(tab_check)
scrollable_frame_bag = add_scrollable_frame(tab_bag)

# Add tabs
tab_control.add(tab_check, text='Check')
tab_control.add(tab_bag, text='Bag')
tab_control.pack(expand=1, fill="both")

# Add reset button to each tab
add_reset_button(tab_check, "check")
add_reset_button(tab_bag, "bag")


# Check Tab
lbl_space = create_button_with_label(scrollable_frame_check, "Check Space", lambda: check_space(lbl_space, lbl_space_message))
lbl_space_message = tk.Label(scrollable_frame_check, text="rpool free storage should be > 500GB. If not, click Remove Bags", wraplength=300)
lbl_space_message.pack(padx=10, pady=5)  

lbl_remove_bags = create_button_with_label(scrollable_frame_check, "Remove Bags", lambda: run_command("rm /data/aviary/local/*.bag", lbl_remove_bags))
lbl_cluster1 = create_button_with_label(scrollable_frame_check, "Check Cluster Connection 1", lambda: run_command("ping -c 1 chiron.seas.unipenn.edu", lbl_cluster1))
lbl_cluster2 = create_button_with_label(scrollable_frame_check, "Check Cluster Connection 2", lambda: run_command("ping -c 1 neowise.seas.unipenn.edu", lbl_cluster2))
lbl_cluster_login = create_button_with_label(scrollable_frame_check, "Check Cluster Login", lambda: run_command("ssh birdproc@chiron.seas.unipenn.edu 'md5sum /mnt/bird_home/birdproc/login_verification'", lbl_cluster_login))


# Bag Tab
def list_available_bags():
    global YEAR
    year_input = year_entry.get()
    if not year_input.isdigit() or not (2020 <= int(year_input) <= 2030):
        list_bags_output.config(text="Please enter a valid year (2020-2030)", fg="red")
        return

    YEAR = year_input
    command = f"ssh birdproc@chiron.seas.unipenn.edu \"ls -lah /mnt/bird_home/birds/data/aviary/{YEAR}/bags/\""
    run_command(command, list_bags_output)

def copy_bag_from_cluster():
    global MONTH, DAY, DATE, YEAR
    month_input = month_entry.get()
    day_input = day_entry.get()
    if not (month_input.isdigit() and day_input.isdigit()) or not (1 <= int(month_input) <= 12) or not (1 <= int(day_input) <= 31):
        copy_bag_output.config(text="Please enter again, make sure to add 0 before a single-digit number", fg="red")
        return

    MONTH, DAY = month_input.zfill(2), day_input.zfill(2)
    DATE = f"{YEAR}-{MONTH}-{DAY}"
    command = f"scp birdproc@chiron.seas.unipenn.edu:/mnt/bird_home/birds/data/aviary/{YEAR}/bags/aviary_{DATE}* /data/aviary/local/."
    run_command(command, copy_bag_output)



def check_bag_integrity():
    global BAG_PATH, DATE
    if 'DATE' not in globals():
        DATE = None
    if DATE is None:
        check_bag_output.config(text="DATE is missing", fg="red")
        return

    BAG_PATH = f"/data/aviary/local/aviary_{DATE}*"
    command = f"rosbag info {BAG_PATH}"
    run_command(command, check_bag_output)
    
# 4. Estimating Relevant Times
def estimate_times():
    start_time = start_time_entry.get()
    duration = duration_entry.get()
    try:
        start_time_int = int(start_time) * 60
        duration_int = int(duration) * 60
        estimate_times_output_label.config(text=f"START_TIME={start_time_int}\nDURATION={duration_int}", fg="black")
        global START_TIME, DURATION
        START_TIME, DURATION = start_time_int, duration_int
    except ValueError:
        estimate_times_output_label.config(text="Please enter valid numbers", fg="red")


def extract_videos():
    global BAG_PATH, START_TIME, DURATION
    if 'BAG_PATH' not in globals():
        BAG_PATH = None
    if 'START_TIME' not in globals():
        START_TIME = None
    if 'DURATION' not in globals():
        DURATION = None

    # Check if all required information is available
    if not all([YEAR, MONTH, DAY, BAG_PATH, START_TIME, DURATION]):
        missing = [var for var in ["YEAR", "MONTH", "DAY", "BAG_PATH", "START_TIME", "DURATION"] if globals()[var] is None]
        extract_videos_output.config(text="\n".join([f"{m} is missing" for m in missing]), fg="red")
        return

    VIDEO_DIR = f"/data/aviary/videos/{YEAR}_{MONTH}_{DAY}_ST{START_TIME}_DUR{DURATION}"
    command = f"mkdir -p {VIDEO_DIR} && roslaunch ffmpeg_image_transport_tools split_bag.launch bag:={BAG_PATH} out_file_base:={VIDEO_DIR}/video_ write_time_stamps:=true convert_to_mp4:=true start_time:={START_TIME} duration:={DURATION}"
    run_command(command, extract_videos_output)


# List Available Bags Section
list_bags_frame = tk.Frame(scrollable_frame_bag)  # Add to scrollable_frame_bag
list_bags_frame.pack(pady=10)
tk.Button(list_bags_frame, text="List Available Bags", command=list_available_bags).pack()
tk.Label(list_bags_frame, text="Year: ").pack(side=tk.LEFT)
year_entry = tk.Entry(list_bags_frame)
year_entry.pack(side=tk.LEFT)
list_bags_output = tk.Label(list_bags_frame, text="", wraplength=500)
list_bags_output.pack()

# Copy Bag From Cluster Section
copy_bag_frame = tk.Frame(scrollable_frame_bag)  # Add to scrollable_frame_bag
copy_bag_frame.pack(pady=10)
tk.Button(copy_bag_frame, text="Copy Bag From Cluster", command=copy_bag_from_cluster).pack()
tk.Label(copy_bag_frame, text="Month (01 to 12): ").pack(side=tk.LEFT)
month_entry = tk.Entry(copy_bag_frame, width=3)
month_entry.pack(side=tk.LEFT)
tk.Label(copy_bag_frame, text="Day (01 to 31): ").pack(side=tk.LEFT)
day_entry = tk.Entry(copy_bag_frame, width=3)
day_entry.pack(side=tk.LEFT)
copy_bag_output = tk.Label(copy_bag_frame, text="", wraplength=500)
copy_bag_output.pack()

# Check Bag Integrity and Info Section
check_bag_frame = tk.Frame(scrollable_frame_bag)  # Add to scrollable_frame_bag
check_bag_frame.pack(pady=10)
tk.Button(check_bag_frame, text="Check Bag Integrity and Info", command=check_bag_integrity).pack()
check_bag_output = tk.Label(check_bag_frame, text="", wraplength=500)
check_bag_output.pack()

# Estimating Relevant Times Section

estimate_times_btn = tk.Button(scrollable_frame_bag, text="Estimate Relevant Times", command=estimate_times)
estimate_times_btn.pack()

start_time_label = tk.Label(scrollable_frame_bag, text="Start Time (minutes into bag): ")
start_time_label.pack()

start_time_entry = tk.Entry(scrollable_frame_bag)
start_time_entry.pack()

duration_label = tk.Label(scrollable_frame_bag, text="Duration (in minutes): ")
duration_label.pack()

duration_entry = tk.Entry(scrollable_frame_bag)
duration_entry.pack()

estimate_times_output_label = tk.Label(scrollable_frame_bag, text="")
estimate_times_output_label.pack()
# Extracting Videos Section
extract_videos_frame = tk.Frame(scrollable_frame_bag)  # Add to scrollable_frame_bag
extract_videos_frame.pack(pady=10)
tk.Button(extract_videos_frame, text="Extract Videos", command=extract_videos).pack()
extract_videos_output = tk.Label(extract_videos_frame, text="", wraplength=500)
extract_videos_output.pack()


root.mainloop()