from typing import List
import argparse
import sys
import logging

import os
import json
from functools import reduce

import jsonschema


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["merge", "unmerge", "sort_skills"])
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("-d", "--dir", metavar="DIR", default=os.getcwd())
    parser.add_argument(
        "-s",
        "--schema",
        metavar="SCHEMA_FILE",
        default=os.path.dirname(__file__) + "/schema.json",
    )
    return parser.parse_args()


def load_schema(schema_path):
    with open(schema_path, "r") as f:
        return json.load(f)


def validate_resume(resume, schema):
    try:
        jsonschema.validate(instance=resume, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        logging.exception("invalid resume")
        sys.exit(1)
    else:
        logging.info("json resume is valid")


def load_resumes(dir_: str, schema):
    logging.info("loading resumes")
    files = {}
    for file in os.listdir(dir_):
        sp = os.path.splitext(file)
        if len(sp) == 2 and len(sp[0]) == 2 and sp[1] == ".json":
            logging.info("found resume language file: %s" % file)
            with open(dir_ + "/" + file, "r") as f:
                resume = json.load(f)
                validate_resume(resume, schema)
                files[sp[0]] = resume
        else:
            logging.debug("%s is not a resume langage file" % file)
    return files


def write_resumes(dir_, files):
    for lang, resume in files.items():
        filename = lang + ".json"
        logging.info("writing output lang to %s" % filename)
        with open(dir_ + "/" + filename, "w") as f:
            json.dump(resume, f, indent=4)


def merge(dir_: str, schema):
    def rec_merge(files):
        def intersec(sets):
            return reduce(lambda a, b: a & b, sets)

        def union(sets):
            return reduce(lambda a, b: a | b, sets)

        if len(files) == 1:
            return next(iter(files.values()))

        types = [type(node) for node in files.values()]
        if not all([types[0] is type_ for type_ in types[1:]]):
            raise ValueError("Mismatch type between nodes: %s" % str(types))
        elif types[0] is dict:
            keys = [set(f.keys()) for f in files.values()]
            nkeys = sorted(list(union(keys)))
            return {
                nk: rec_merge(
                    {
                        lang: resume[nk]
                        for lang, resume in files.items()
                        if nk in resume
                    }
                )
                for nk in nkeys
            }

        elif types[0] is list:
            lens = [len(f) for f in files.values()]
            if not all([lens[0] == len_ for len_ in lens]):
                raise ValueError(
                    "Mismatch in list lengths: %s" % str(list(files.values()))
                )
            else:
                return [
                    rec_merge({lang: e for lang, e in zip(files.keys(), el)})
                    for el in zip(*list(files.values()))
                ]
        else:
            values = list(files.values())
            if all([values[0] == value for value in values]):
                return values[0]
            else:
                return {"@" + lang: e for lang, e in files.items()}

    def write_output(out, dir_, filename="resume.json"):
        logging.info("writing output to %s" % filename)
        with open(dir_ + "/" + filename, "w") as f:
            json.dump(out, f, indent=4)

    files = load_resumes(dir_, schema)
    logging.info("merging")
    out = rec_merge(files)
    write_output(out, dir_)


def sort_skills(dir_: str, schema):

    logging.info("sorting skills")
    files = load_resumes(dir_, schema)
    for resume in files.values():
        if "skills" in resume:
            resume["skills"].sort(key=lambda a: a["name"])

    write_resumes(dir_, files)


def unmerge(dir_: str, schema):
    logging.info("unmerging")

    def load_merged_resume(dir_):
        logging.info("loading merged resume")
        with open(dir_ + "/resume.json", "r") as f:
            return json.load(f)

    def is_lang_key(k: str):
        return k[0] == "@" and len(k) == 3

    def read_langs(in_) -> List[str]:
        logging.debug("reading langs")
        if (
            "meta" in in_
            and "lang" in in_["meta"]
            and len(in_["meta"]["lang"]) > 0
        ):
            return list(in_["meta"]["lang"].values())
        else:
            raise ValueError("Could not find .meta.lang or is empty")

    def rec_unmerge(in_, langs):
        type_ = type(in_)
        if type_ is dict:
            are_langs = all([is_lang_key(k) for k in in_.keys()])
            if are_langs:
                return {lang[1:]: v for lang, v in in_.items()}
            else:
                out = {lang: {} for lang in langs}
                for k, v in in_.items():
                    r = rec_unmerge(v, langs)
                    for lang in langs:
                        out[lang][k] = r[lang]
                return out

        elif type_ is list:
            out = {lang: [] for lang in langs}
            for v in in_:
                r = rec_unmerge(v, langs)
                for lang in langs:
                    out[lang].append(r[lang])
            return out
        else:
            return {lang: in_ for lang in langs}

    in_ = load_merged_resume(dir_)
    logging.info("unmerging")
    langs = read_langs(in_)
    logging.debug("langs are %s" % str(langs))
    files = rec_unmerge(in_, langs)
    write_resumes(dir_, files)


if __name__ == "__main__":
    args = parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    logging.debug("Parsed arguments : %s" % str(args))
    schema = load_schema(args.schema)
    globals()[args.action](args.dir, schema)
