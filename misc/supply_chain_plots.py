"""Provides generic plotting routines for the supply chain model."""

from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.text as txt
import matplotlib.pyplot as plt


def mysave(fig, froot, mode="png"):
    """Custom save method."""
    assert mode in ["png", "eps", "pdf", "all"]
    fileName = Path(froot).name
    padding = 0.1
    dpiVal = 200
    legs = []
    for a in fig.get_axes():
        addLeg = a.get_legend()
        if addLeg is not None:
            legs.append(a.get_legend())
    ext = []
    if mode == "png" or mode == "all":
        ext.append("png")
    if mode == "eps":  # or mode == 'all':
        ext.append("eps")
    if mode == "pdf" or mode == "all":
        ext.append("pdf")

    for sfx in ext:
        fig.savefig(
            fileName.with_suffix(sfx),
            format=sfx,
            pad_inches=padding,
            bbox_inches="tight",
            dpi=dpiVal,
            bbox_extra_artists=legs,
        )


titleSize = 24  # 40 #38
axLabelSize = 20  # 38 #36
tickLabelSize = 18  # 30 #28
ganttTick = 18
legendSize = tickLabelSize + 2
textSize = legendSize - 2
deltaShow = 4
linewidth = 3


def myformat(
    ax,
    linewidth=linewidth,
    xticklabel=tickLabelSize,
    yticklabel=tickLabelSize,
    mode="save",
):
    """Custom axes formatter method."""
    assert isinstance(mode, str)
    assert mode.lower() in ["save", "show"], "Unknown mode"

    def myformat(
        myax,
        linewidth=linewidth,
        xticklabel=xticklabel,
        yticklabel=yticklabel,
    ):
        if mode.lower() == "show":
            for i in myax.get_children():  # Gets EVERYTHING!
                if isinstance(i, txt.Text):
                    i.set_size(textSize + 3 * deltaShow)

            for i in myax.get_lines():
                if i.get_marker() == "D":
                    continue  # Don't modify baseline diamond
                i.set_linewidth(linewidth)
                # i.set_markeredgewidth(4)
                i.set_markersize(10)

            leg = myax.get_legend()
            if leg is not None:
                for t in leg.get_texts():
                    t.set_fontsize(legendSize + deltaShow + 6)
                th = leg.get_title()
                if th is not None:
                    th.set_fontsize(legendSize + deltaShow + 6)

            myax.set_title(
                myax.get_title(),
                size=titleSize + deltaShow,
                weight="bold",
            )
            myax.set_xlabel(
                myax.get_xlabel(),
                size=axLabelSize + deltaShow,
                weight="bold",
            )
            myax.set_ylabel(
                myax.get_ylabel(),
                size=axLabelSize + deltaShow,
                weight="bold",
            )
            myax.tick_params(labelsize=tickLabelSize + deltaShow)
            myax.patch.set_linewidth(3)
            for i in myax.get_xticklabels():
                i.set_size(tickLabelSize + deltaShow)
            for i in myax.get_xticklines():
                i.set_linewidth(3)
            for i in myax.get_yticklabels():
                i.set_size(yticklabel + deltaShow)
            for i in myax.get_yticklines():
                i.set_linewidth(3)

        elif mode.lower() == "save":
            for i in myax.get_children():  # Gets EVERYTHING!
                if isinstance(i, txt.Text):
                    i.set_size(textSize)

            for i in myax.get_lines():
                if i.get_marker() == "D":
                    continue  # Don't modify baseline diamond
                i.set_linewidth(linewidth)
                # i.set_markeredgewidth(4)
                i.set_markersize(10)

            leg = myax.get_legend()
            if leg is not None:
                for t in leg.get_texts():
                    t.set_fontsize(legendSize)
                th = leg.get_title()
                if th is not None:
                    th.set_fontsize(legendSize)

            myax.set_title(myax.get_title(), size=titleSize, weight="bold")
            myax.set_xlabel(myax.get_xlabel(), size=axLabelSize, weight="bold")
            myax.set_ylabel(myax.get_ylabel(), size=axLabelSize, weight="bold")
            myax.tick_params(labelsize=tickLabelSize)
            myax.patch.set_linewidth(3)
            for i in myax.get_xticklabels():
                i.set_size(xticklabel)
            for i in myax.get_xticklines():
                i.set_linewidth(3)
            for i in myax.get_yticklabels():
                i.set_size(yticklabel)
            for i in myax.get_yticklines():
                i.set_linewidth(3)

    if isinstance(ax, list):
        for i in ax:
            myformat(i)
    else:
        myformat(ax)


def initFigAxis(figx=12, figy=9):
    """Initializes the Figure and Axes."""
    fig = plt.figure(figsize=(figx, figy))
    ax = fig.add_subplot(111)
    return fig, ax


def waterfall_plot(x, y, bottom, color, bar_text, fname=None):
    """Waterfall plot comparing European andUS manufactining costs."""

    fig, ax = initFigAxis()

    h = ax.bar(x, y, bottom=bottom, color=color, edgecolor="k")

    ax.get_yaxis().set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ",")),
    )
    ax.set_ylabel("Capital Expenditures, $/kW")
    title = (
        "Comparison of different cost premiums between"
        "\nimported and domestically manufactured components"
    )
    ax.set_title(title)

    h[3].set_linestyle("--")
    h[3].set_linewidth(1.75)
    h[3].set_edgecolor("k")

    ax.text(
        x[1],
        2000,
        bar_text["transit"],
        horizontalalignment="center",
    )
    ax.text(
        x[2],
        2000,
        bar_text["factory"],
        horizontalalignment="center",
    )
    ax.text(
        x[3],
        2000,
        bar_text["margin"],
        horizontalalignment="center",
    )

    if fname is not None:
        myformat(ax)
        mysave(fig, fname)
        plt.close()


def area_time_plot(x, y, color, fname=None):
    """Area plot showing changing component cost over time."""

    fig, ax = initFigAxis()

    y0 = np.zeros(len(x))

    y_init = 0
    y_init = np.sum([v[0] for k, v in y.items()])

    for k, v in y.items():
        y1 = [yi + vi for yi, vi in zip(y0, v)]
        ax.fill_between(x, y0 / y_init, y1 / y_init, color=color[k], label=k)
        ax.plot(x, y1 / y_init, "w")
        y0 = y1

    # Define margin
    ax.fill_between(
        x,
        y1 / y_init,
        np.ones(len(x)),
        color=color["Cost margin"],
        label="Margin",
    )

    final_margin = round(100 * (1 - y1[-1] / y_init), 1)

    y_margin = (1 + y1[-1] / y_init) / 2

    margin_text = (
        f"   {final_margin}"
        "% CapEx margin relative to "
        "\n   European imports can cover "
        "\n   local differences in wages, "
        "\n   taxes, financing, etc"
    )

    right_bound = 2030.5
    right_spline_corr = 0.2

    ax.plot([2030, right_bound], [y_margin, y_margin], "k")
    ax.text(right_bound, y_margin, margin_text, verticalalignment="center")
    ax.spines["right"].set_position(("data", right_bound - right_spline_corr))
    ax.spines["top"].set_bounds(2022.65, right_bound - right_spline_corr)
    ax.spines["bottom"].set_bounds(2022.65, right_bound - right_spline_corr)

    ax.text(2023, -0.215, "(Fully \nimported)", horizontalalignment="center")
    ax.text(2030, -0.215, "(Fully \ndomestic)", horizontalalignment="center")

    ax.set_yticklabels([-20, 0, 20, 40, 60, 80, 100])

    ax.legend(loc=(1, 0.05))

    ax.set_ylabel(
        "CapEx breakdown relative to \ncomponents imported from Europe, %",
    )

    if fname is not None:
        myformat(ax)
        mysave(fig, fname)
        plt.close()
