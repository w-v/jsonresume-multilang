# jsonresume-multilang

This is a hacky way to maintain multiple [jsonresume](https://jsonresume.org/) in different languages without duplicating too much information    

## Idea

The idea is to have a single json resume file where entries for each languages are specified in a dictionary with `@lang`, all entries that do not require translation remain unchanged:

`resume.json`
```
{
    "basics": {
        "email": "john@doe.com",
        "image": "",
        "label": {
            "@fr": "Développeur Python",
            "@en": "Python Developer"
        }
    },
    "meta": {
        "lang": {
            "@fr": "fr",
            "@en": "en"
        },
        "version": "v1.0.0"
    }
}
```

This file is not a valid json resume, and its sole purpose is to be edited and then **unmerged** into valid, single language json resumes:

```
jsonresume-multilang unmerge
```

`fr.json`
```
{
    "basics": {
        "email": "john@doe.com",
        "image": "",
        "label": "Développeur Python"
    },
    "meta": {
        "lang": "fr",
        "version": "v1.0.0"
    },
}
```

`en.json`
```
{
    "basics": {
        "email": "john@doe.com",
        "image": "",
        "label": "Python Developer"
    },
    "meta": {
        "lang": "en",
        "version": "v1.0.0"
    },
}
```

Single language files can also be **merged** back to the multilingual `resume.json`:

```
jsonresume-multilang merge
```

**Warning**

The `meta.lang` section (see above examples) **is required** in order to identify language versions

## Installation

Download or clone the repo, and in it run

```
pip install .
```

This will install the `jsonresume-multilang` script


## Usage

```
usage: jsonresume_multilang.py [-h] [-v] [-d DIR] [-s SCHEMA_FILE] {merge,unmerge,sort_skills}

Merge or unmerge json resume files in multiple languages into one

positional arguments:
  {merge,unmerge,sort_skills}
                        merge: merge multiple valid single language json resumes into one

                        unmerge: inverse operation

                        sort_skills: sort skills of single language json resumes in alphabetical order

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase logging verbosity
  -d DIR, --dir DIR     input and output directory for json resume files, defaults to current directory
  -s SCHEMA_FILE, --schema SCHEMA_FILE
                        json resume schema used for validation, defaults to v1.0.0
```

## Issues

### List order

When merging, lists of corresponding entries for language files have to be in the same order    
For example this won't work:

`fr`
```
{
    "skills": [
        {
            "keywords": [],
            "level": "",
            "name": "Publication académique"
        },
        {
            "keywords": [],
            "level": "",
            "name": "Animation 3D"
        }
    ]
}
```

`en`
```
{
    "skills": [
        {
            "keywords": [],
            "level": "",
            "name": "3D Animation"
        },
        {
            "keywords": [],
            "level": "",
            "name": "Academic Publishing"
        }
    ]
}
```

If you imported your json resume from LinkedIn with [joshuatz/linkedin-to-jsonresume](https://github.com/joshuatz/linkedin-to-jsonresume), skills can be in different orders for different languages eventhough they are the same, for this special purpose you can use:
```
jsonresume-multilang sort_skills
```

