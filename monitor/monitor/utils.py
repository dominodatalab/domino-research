import pandas as pd  # type: ignore
import numpy as np  # type: ignore

SAMPLE_DF_N_COLS_PER_TYPE = 2
SAMPLE_DF_N_PER_COL = 1000
SAMPLE_DF_MIN_INT = -100
SAMPLE_DF_MAX_INT = 100
SAMPLE_DF_STRING_DOMAINS = ["eeny", "meeny", "miny", "moe"]

SAMPLE_DF_NULL_PERCENTS = {"int_0": 0.1, "float_0": 0.2, "str_0": 0.3}


def generate_sample_dataframe() -> pd.DataFrame:

    ints_df = pd.DataFrame(
        np.random.randint(
            SAMPLE_DF_MIN_INT,
            SAMPLE_DF_MAX_INT,
            size=(SAMPLE_DF_N_PER_COL, SAMPLE_DF_N_COLS_PER_TYPE),
        ),
        columns=[f"int_{n}" for n in range(SAMPLE_DF_N_COLS_PER_TYPE)],
    )

    positive_ints_df = pd.DataFrame(
        np.random.randint(
            0,
            SAMPLE_DF_MAX_INT,
            size=(SAMPLE_DF_N_PER_COL, SAMPLE_DF_N_COLS_PER_TYPE),
        ),
        columns=[
            f"positive_int_{n}" for n in range(SAMPLE_DF_N_COLS_PER_TYPE)
        ],
    )

    floats_df = pd.DataFrame(
        np.random.random(
            size=(SAMPLE_DF_N_PER_COL, SAMPLE_DF_N_COLS_PER_TYPE)
        ),
        columns=[f"float_{n}" for n in range(SAMPLE_DF_N_COLS_PER_TYPE)],
    )

    strings_df = pd.DataFrame(
        np.random.choice(
            SAMPLE_DF_STRING_DOMAINS,
            size=(SAMPLE_DF_N_PER_COL, SAMPLE_DF_N_COLS_PER_TYPE),
        ),
        columns=[f"str_{n}" for n in range(SAMPLE_DF_N_COLS_PER_TYPE)],
    )

    mixed_df = pd.DataFrame(
        np.random.choice(
            np.array([SAMPLE_DF_STRING_DOMAINS[0], 1, 2.0], dtype="object"),
            size=(SAMPLE_DF_N_PER_COL, SAMPLE_DF_N_COLS_PER_TYPE),
        ),
        columns=[f"mixed_{n}" for n in range(SAMPLE_DF_N_COLS_PER_TYPE)],
    )

    full_df = pd.concat(
        [ints_df, positive_ints_df, floats_df, strings_df, mixed_df], axis=1
    )

    for target_col, target_frac in SAMPLE_DF_NULL_PERCENTS.items():
        indeces = np.random.choice(
            range(SAMPLE_DF_N_PER_COL),
            size=int(SAMPLE_DF_N_PER_COL * target_frac),
            replace=False,
        )
        full_df.loc[indeces, target_col] = None

    return full_df
