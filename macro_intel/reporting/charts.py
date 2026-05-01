from __future__ import annotations

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def _format_dates() -> None:
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))


def plot_normalized_and_ratio(
    normalized_df: pd.DataFrame,
    raw_df: pd.DataFrame,
    *,
    left_label: str,
    right_label: str,
    left_column: str,
    right_column: str,
    ratio_column: str,
    figure_title: str,
    ratio_title: str,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig.suptitle(figure_title, fontsize=16)
    ax1.plot(normalized_df.index, normalized_df[left_column], label=left_label)
    ax1.plot(normalized_df.index, normalized_df[right_column], label=right_label)
    ax1.legend()
    ax1.grid(True, linestyle=":")
    ax1.set_title("Normalized Price (Z-Score)")
    ax2.plot(raw_df.index, raw_df[ratio_column], label=ratio_column)
    ax2.legend()
    ax2.grid(True, linestyle=":")
    ax2.set_title(ratio_title)
    _format_dates()
    return fig, (ax1, ax2)


def plot_dual_axis_line(
    df: pd.DataFrame,
    *,
    left_column: str,
    right_column: str,
    figure_title: str,
    left_title: str,
    left_color: str = "purple",
    right_color: str = "blue",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    fig, ax1 = plt.subplots(figsize=(15, 6))
    fig.suptitle(figure_title, fontsize=16)
    ax1.plot(df.index, df[left_column], label=left_column, color=left_color)
    ax1.set_title(left_title)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle=":")
    ax2 = ax1.twinx()
    ax2.plot(df.index, df[right_column], label=right_column, color=right_color, alpha=0.7)
    ax2.legend(loc="upper right")
    _format_dates()
    return fig, (ax1, ax2)


def plot_dual_axis_bar(
    df: pd.DataFrame,
    *,
    line_column: str,
    bar_column: str,
    figure_title: str,
    line_title: str,
    bar_title: str,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True)
    fig.suptitle(figure_title, fontsize=16)
    ax1.plot(df.index, df[line_column], label=line_column, color="purple")
    ax1.set_title(line_title)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle=":")
    ax2.bar(df.index, df[bar_column], label=bar_column, color="blue", alpha=0.7, width=3)
    ax2.axhline(0, color="black", linestyle="--", linewidth=1)
    ax2.set_title(bar_title)
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle=":")
    _format_dates()
    return fig, (ax1, ax2)


def plot_rolling_correlation(
    df: pd.DataFrame,
    *,
    short_column: str = "Corr_30D",
    long_column: str = "Corr_90D",
    figure_title: str,
    plot_title: str,
    reference_level: float = 0.0,
) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(15, 6))
    fig.suptitle(figure_title, fontsize=16)
    ax.plot(df.index, df[short_column], label=short_column, color="orange", alpha=0.7)
    ax.plot(df.index, df[long_column], label=long_column, color="darkblue", linewidth=2)
    ax.axhline(reference_level, color="black", linestyle="--", linewidth=1)
    ax.set_title(plot_title)
    ax.legend()
    ax.grid(True, linestyle=":")
    _format_dates()
    return fig, ax


def plot_volatility_dashboard(
    df: pd.DataFrame,
    *,
    iv_rank_columns: tuple[str, str],
    vrp_columns: tuple[str, str],
    figure_title: str,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig.suptitle(figure_title, fontsize=16)
    ax1.plot(df.index, df[iv_rank_columns[0]], label=iv_rank_columns[0])
    ax1.plot(df.index, df[iv_rank_columns[1]], label=iv_rank_columns[1])
    ax1.axhline(50, color="black", linestyle="--", linewidth=1)
    ax1.set_title("Implied Volatility Rank (252-Day)")
    ax1.legend()
    ax1.grid(True, linestyle=":")
    ax2.plot(df.index, df[vrp_columns[0]], label=vrp_columns[0])
    ax2.plot(df.index, df[vrp_columns[1]], label=vrp_columns[1])
    ax2.axhline(0, color="black", linestyle="--", linewidth=1)
    ax2.set_title("Volatility Risk Premium")
    ax2.legend()
    ax2.grid(True, linestyle=":")
    _format_dates()
    return fig, (ax1, ax2)
