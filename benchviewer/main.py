import os.path
import json

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
from src.backend import *
from datetime import datetime
import logging


def init():
    read_mqtbench_all_zip()
    init_database()

    # logging.basicConfig(filename="/local/mqtbench/downloads.log", level=logging.INFO)


init()
app = Flask(__name__)

PREFIX = "/mqtbench/"


@app.route(f"{PREFIX}/", methods=["POST", "GET"])
@app.route(f"{PREFIX}/index", methods=["POST", "GET"])
def index():
    """Return the index.html file together with the benchmarks and nonscalable benchmarks."""

    return render_template(
        "index.html",
        benchmarks=benchmarks,
        nonscalable_benchmarks=nonscalable_benchmarks,
    )


@app.route(f"{PREFIX}/get_pre_gen", methods=["POST", "GET"])
def download_pre_gen_zip():
    directory = "./static/files/qasm_output/"
    filename = "MQTBench_all.zip"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    return send_from_directory(
        directory=directory,
        path=filename,
        as_attachment=True,
        mimetype="application/zip",
        download_name="MQTBench_all.zip",
    )


@app.route(f"{PREFIX}/download", methods=["POST", "GET"])
def download_data():
    """Triggers the downloading process of all benchmarks according to the user's input."""
    if request.method == "POST":
        data = request.form
        prepared_data = prepareFormInput(data)
        print("raw data :", data)
        print("prepared input data :", prepared_data)
        file_paths = get_selected_file_paths(prepared_data)
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        if file_paths:
            return app.response_class(
                generate_zip_ephemeral_chunks(file_paths),
                mimetype="application/zip",
                headers={
                    "Content-Disposition": 'attachment; filename="MQTBench_{}.zip"'.format(
                        timestamp
                    )
                },
                direct_passthrough=True,
            )

    return render_template(
        "index.html",
        benchmarks=benchmarks,
        nonscalable_benchmarks=nonscalable_benchmarks,
    )


@app.route(f"{PREFIX}/legal")
def legal():
    """Return the legal.html file."""

    return render_template("legal.html")


@app.route(f"{PREFIX}/description")
def description():
    """Return the description.html file in which the file formats are described."""

    return render_template("description.html")


@app.route(f"{PREFIX}/benchmark_description")
def benchmark_description():
    """Return the benchmark_description.html file together in which all benchmark algorithms
    are described in detail.
    """

    return render_template("benchmark_description.html")


@app.route(f"{PREFIX}/get_num_benchmarks", methods=["POST"])
def get_num_benchmarks():

    if request.method == "POST":
        data = request.form
        prepared_data = prepareFormInput(data)
        file_paths = get_selected_file_paths(prepared_data)
        num = len(file_paths)
        print("Num benchmarks: ", num)
        data = {"num_selected": num}
        return jsonify(data)
    else:
        data = {"num_selected": 0}

        return jsonify(data)


def get_num_algo_layer_benchmarks(benchmark_name, config_entry):
    if (
        benchmark_name == "groundstate"
        or benchmark_name == "excitedstate"
        or benchmark_name == "shor"
    ):
        return len(config_entry["instances"])
    elif benchmark_name == "routing" or benchmark_name == "tsp":
        return config_entry["max_nodes"] - config_entry["min_nodes"]
    elif benchmark_name == "pricingcall" or benchmark_name == "pricingput":
        return config_entry["max_uncertainty"] - config_entry["min_uncertainty"]
    elif benchmark_name == "hhl":
        return config_entry["max_index"] - config_entry["min_index"]
    else:
        return False


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
