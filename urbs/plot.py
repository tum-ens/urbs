import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from random import random
from .data import COLORS
from .input import get_input
from .output import get_constants, get_timeseries
from .pyomoio import get_entity
from .util import is_string


def sort_plot_elements(elements):
    """Sort timeseries for plotting

    Sorts the timeseries (created, consumed) ascending with variance.
    It places base load at the bottom and peak load at the top.
    This enhances clearity and readability of the plots.

    Args:
        elements: timeseries of created or consumed

    Returns:
        elements_sorted: sorted timeseries of created or consumed
    """
    # no need of sorting the columns if there's only one
    if len(elements.columns) < 2:
        return elements

    # calculate standard deviation
    std = pd.DataFrame(np.zeros_like(elements.tail(1)),
                       index=elements.index[-1:]+1,
                       columns=elements.columns)
    # calculate mean
    mean = pd.DataFrame(np.zeros_like(elements.tail(1)),
                        index=elements.index[-1:]+1,
                        columns=elements.columns)
    # calculate quotient
    quotient = pd.DataFrame(
        np.zeros_like(elements.tail(1)),
        index=elements.index[-1:]+1,
        columns=elements.columns)

    for col in std.columns:
        std[col] = np.std(elements[col])
        mean[col] = np.mean(elements[col])
        quotient[col] = std[col] / mean[col]
    # fill nan values (due to division by 0)
    quotient = quotient.fillna(0)
    # sort created/consumed ascencing with quotient i.e. base load first
    elements = elements.append(quotient)
    new_columns = elements.columns[elements.ix[elements.last_valid_index()]
                                           .argsort()]
    elements_sorted = elements[new_columns][:-1]

    return elements_sorted


def plot(prob, com, sit, dt, timesteps, timesteps_plot,
         power_name='Power', energy_name='Energy',
         power_unit='MW', energy_unit='MWh', time_unit='h',
         figure_size=(16, 12)):
    """Plot a stacked timeseries of commodity balance and storage.

    Creates a stackplot of the energy balance of a given commodity, together
    with stored energy in a second subplot.

    Args:
        prob: urbs model instance
        com: commodity name to plot
        sit: site name to plot
        dt: length of each time step (unit: hours)
        timesteps: modelled timesteps
        timesteps_plot: timesteps to be plotted

        power_name: optional string for 'power' label; default: 'Power'
        power_unit: optional string for unit; default: 'MW'
        energy_name: optional string for 'energy' label; default: 'Energy'
        energy_unit: optional string for storage plot; default: 'MWh'
        time_unit: optional string for time unit label; default: 'h'
        figure_size: optional (width, height) tuple in inch; default: (16, 12)

    Returns:
        fig: figure handle
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    if timesteps is None:
        # default to all simulated timesteps
        timesteps = sorted(get_entity(prob, 'tm').index)

    # convert timesteps to hour series for the plots
    hoursteps = timesteps * dt[0]
    hoursteps_plot = timesteps_plot * dt[0]

    if is_string(sit):
        # wrap single site in 1-element list for consistent behaviour
        sit = [sit]

    (created, consumed, stored, imported, exported,
     dsm) = get_timeseries(prob, com, sit, timesteps)

    costs, cpro, ctra, csto = get_constants(prob)

    # move retrieved/stored storage timeseries to created/consumed and
    # rename storage columns back to 'storage' for color mapping
    created = created.join(stored['Retrieved'])
    consumed = consumed.join(stored['Stored'])
    created.rename(columns={'Retrieved': 'Storage'}, inplace=True)
    consumed.rename(columns={'Stored': 'Storage'}, inplace=True)

    # only keep storage content in storage timeseries
    stored = stored['Level']

    # add imported/exported timeseries
    created = created.join(imported)
    consumed = consumed.join(exported)

    # move demand to its own plot
    demand = consumed.pop('Demand')
    original = dsm.pop('Unshifted')
    deltademand = dsm.pop('Delta')
    try:
        # detect whether DSM could be used in this plot
        # if so, show DSM subplot (even if delta == 0 for the whole time)
        df_dsm = get_input(prob, 'dsm')
        plot_dsm = df_dsm.loc[(sit, com),
                              ['cap-max-do', 'cap-max-up']].sum().sum() > 0
    except (KeyError, TypeError):
        plot_dsm = False

    # remove all columns from created which are all-zeros in both created and
    # consumed (except the last one, to prevent a completely empty frame)
    for col in created.columns:
        if not created[col].any() and len(created.columns) > 1:
            if col not in consumed.columns or not consumed[col].any():
                created.pop(col)

    # remove all columns from consumed which are all-zeros in both created and
    # consumed (except the last one, to prevent a completely empty frame)
    for col in consumed.columns:
        if not consumed[col].any() and len(consumed.columns) > 1:
            if col not in created.columns or not created[col].any():
                consumed.pop(col)

    # sorting plot elements
    created = sort_plot_elements(created)
    consumed = sort_plot_elements(consumed)

    # FIGURE
    fig = plt.figure(figsize=figure_size)
    all_axes = []
    if plot_dsm:
        gs = mpl.gridspec.GridSpec(3, 1, height_ratios=[3, 1, 1], hspace=0.05)
    else:
        gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[2, 1], hspace=0.05)

    # STACKPLOT
    ax0 = plt.subplot(gs[0])
    all_axes.append(ax0)

    # PLOT CONSUMED

    # stack plot for consumed commodities (divided by dt for power)
    sp00 = ax0.stackplot(hoursteps[1:],
                         -consumed.values.T/dt[0],
                         labels=tuple(consumed.columns),
                         linewidth=0.15)
    # color
    for k, commodity in enumerate(consumed.columns):
        commodity_color = to_color(commodity)

        sp00[k].set_facecolor(commodity_color)
        sp00[k].set_edgecolor((.5, .5, .5))

    # PLOT CREATED

    # stack plot for created commodities (divided by dt for power)
    sp0 = ax0.stackplot(hoursteps[1:],
                        created.values.T/dt[0],
                        labels=tuple(created.columns),
                        linewidth=0.15)

    for k, commodity in enumerate(created.columns):
        commodity_color = to_color(commodity)

        sp0[k].set_facecolor(commodity_color)
        sp0[k].set_edgecolor(to_color('Decoration'))

    # label
    ax0.set_title('Commodity balance of {} in {}'.format(com, ', '.join(sit)))
    ax0.set_ylabel('{} ({})'.format(power_name, power_unit))

    # legend
    handles, labels = ax0.get_legend_handles_labels()

    # add "only" consumed commodities to the legend
    for item in consumed.columns[::-1]:
        # if item not in created add to legend, except items
        # from consumed which are all-zeros
        if item in created.columns or consumed[item].any():
            pass
        else:
            # remove item/commodity is not consumed
            item_index = labels.index(item)
            handles.pop(item_index)
            labels.pop(item_index)

    for item in labels:
        if labels.count(item) > 1:
            item_index = labels.index(item)
            handles.pop(item_index)
            labels.pop(item_index)

    lg = ax0.legend(handles=handles[::-1],
                    labels=labels[::-1],
                    frameon=False,
                    loc='upper left',
                    bbox_to_anchor=(1, 1))
    plt.setp(lg.get_patches(), edgecolor=to_color('Decoration'),
             linewidth=0.15)
    plt.setp(ax0.get_xticklabels(), visible=False)

    # PLOT DEMAND

    # line plot for demand (unshifted) commodities (divided by dt for power)
    ax0.plot(hoursteps, original.values/dt[0], linewidth=0.8,
             color=to_color('Unshifted'))

    # line plot for demand (shifted) commodities (divided by dt for power)
    ax0.plot(hoursteps[1:], demand.values/dt[0], linewidth=1.0,
             color=to_color('Shifted'))

    # PLOT STORAGE
    ax1 = plt.subplot(gs[1], sharex=ax0)
    all_axes.append(ax1)

    # stack plot for stored commodities
    try:
        sp1 = ax1.stackplot(hoursteps, stored.values, linewidth=0.15)
    except:
        stored = pd.Series(0, index=hoursteps)
        sp1 = ax1.stackplot(hoursteps, stored.values, linewidth=0.15)
    if plot_dsm:
        # hide xtick labels only if DSM plot follows
        plt.setp(ax1.get_xticklabels(), visible=False)
    else:
        # else add label for time axis
        ax1.set_xlabel('Time in year ({})'.format(time_unit))

    # color & labels
    sp1[0].set_facecolor(to_color('Storage'))
    sp1[0].set_edgecolor(to_color('Decoration'))
    ax1.set_ylabel('{} ({})'.format(energy_name, energy_unit))

    try:
        ax1.set_ylim((0, 0.5 + csto.loc[sit, :, com]['C Total'].sum()))
    except KeyError:
        pass

    # PLOT DEMAND SIDE MANAGEMENT
    if plot_dsm:
        ax2 = plt.subplot(gs[2], sharex=ax0)
        all_axes.append(ax2)

        # bar plot for DSM up-/downshift power (bar width depending on dt)
        ax2.bar(hoursteps,
                deltademand.values/dt[0], width=0.8 * dt[0],
                color=to_color('Delta'),
                edgecolor='none')

        # labels & y-limits
        ax2.set_xlabel('Time in year ({})'.format(time_unit))
        ax2.set_ylabel('{} ({})'.format(power_name, power_unit))

    # make xtick distance duration-dependent
    if len(timesteps_plot) > 26 * 168 / dt[0]:    # time horizon > half a year
        steps_between_ticks = int(168 * 4 / dt[0])  # tick every four weeks
    elif len(timesteps_plot) > 3 * 168 / dt[0]:   # time horizon > three weeks
        steps_between_ticks = int(168 / dt[0])      # tick every week
    elif len(timesteps_plot) > 2 * 24 / dt[0]:    # time horizon > two days
        steps_between_ticks = int(24 / dt[0])       # tick every day
    elif len(timesteps_plot) > 24 / dt[0]:        # time horizon > a day
        steps_between_ticks = int(6 / dt[0])        # tick every six hours
    else:                                         # time horizon <= a day
        steps_between_ticks = int(3 / dt[0])        # tick every three hours

    hoursteps_plot_ = hoursteps_plot[(steps_between_ticks-1):]
    hoursteps_plot_ = hoursteps_plot_[::steps_between_ticks]  # take whole h's
    xticks = np.insert(hoursteps_plot_, 0, hoursteps_plot[0])  # add 1st t.step

    # set limits and ticks for all axes
    for ax in all_axes:
        ax.set_frame_on(False)
        ax.set_xlim(hoursteps_plot[0], hoursteps_plot[-1])
        ax.set_xticks(xticks)
        ax.xaxis.grid(True, 'major', color=to_color('Grid'),
                      linestyle='-')
        ax.yaxis.grid(True, 'major', color=to_color('Grid'),
                      linestyle='-')
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        # group 1,000,000 with commas, but only if maximum or minimum are
        # sufficiently large. Otherwise, keep default tick labels
        ymin, ymax = ax.get_ylim()
        if ymin < -90 or ymax > 90:
            group_thousands = mpl.ticker.FuncFormatter(
                lambda x, pos: '{:0,d}'.format(int(x)))
            ax.yaxis.set_major_formatter(group_thousands)
        else:
            skip_lowest = mpl.ticker.FuncFormatter(
                lambda y, pos: '' if pos == 0 else y)
            ax.yaxis.set_major_formatter(skip_lowest)

    return fig


def result_figures(prob, figure_basename, timesteps, plot_title_prefix=None,
                   plot_tuples=None, plot_sites_name={},
                   periods=None, extensions=None, **kwds):
    """Create plots for multiple periods and sites and save them to files.

    Args:
        prob: urbs model instance
        figure_basename: relative filename prefix that is shared
        plot_title_prefix: (optional) plot title identifier
        plot_tuples: (optional) list of (sit, com) tuples to plot
                     sit may be individual site names or lists of sites
                     default: all demand (sit, com) tuples are plotted
        plot_sites_name: (optional) dict of names for created plots
        periods: (optional) dict of 'period name': timesteps_list items
                 default: one period 'all' with all timesteps is assumed
        extensions: (optional) list of file extensions for plot images
                    default: png, pdf
        **kwds: (optional) keyword arguments are forwarded to urbs.plot()
    """
    # retrieve parameter 'dt' from the model
    dt = get_entity(prob, 'dt')

    # default to all demand (sit, com) tuples if none are specified
    if plot_tuples is None:
        plot_tuples = get_input(prob, 'demand').columns

    # default to all timesteps if no periods are given
    if periods is None:
        periods = {'all': sorted(get_entity(prob, 'tm').index)}

    # default to PNG and PDF plots if no filetypes are specified
    if extensions is None:
        extensions = ['png', 'pdf']

    # create timeseries plot for each demand (site, commodity) timeseries
    for sit, com in plot_tuples:
        # wrap single site name in 1-element list for consistent behaviour
        if is_string(sit):
            help_sit = [sit]
        else:
            help_sit = sit
            sit = tuple(sit)

        try:
            plot_sites_name[sit]
        except:
            plot_sites_name[sit] = str(sit)

        for period, periodrange in periods.items():
            # do the plotting
            fig = plot(prob, com, help_sit, dt, timesteps, periodrange, **kwds)

            # change the figure title
            ax0 = fig.get_axes()[0]
            # if no custom title prefix is specified, use the figure_basename
            if not plot_title_prefix:
                plot_title_prefix = os.path.basename(figure_basename)

            new_figure_title = '{}: {} in {}'.format(
                plot_title_prefix, com, plot_sites_name[sit])
            ax0.set_title(new_figure_title)

            # save plot to files
            for ext in extensions:
                fig_filename = '{}-{}-{}-{}.{}'.format(
                    figure_basename, com, ''.join(
                        plot_sites_name[sit]), period, ext)
                fig.savefig(fig_filename, bbox_inches='tight')
            plt.close(fig)


def to_color(obj=None):
    """Assign a deterministic pseudo-random color to argument.

    If COLORS[obj] is set, return that. Otherwise, create a random color from
    the hash(obj) representation string. For strings, this value depends only
    on the string content, so that same strings always yield the same color.

    Args:
        obj: any hashable object

    Returns:
        a (r, g, b) color tuple if COLORS[obj] is set, otherwise a hexstring
    """
    if obj is None:
        obj = random()
    try:
        color = tuple(rgb/255.0 for rgb in COLORS[obj])
    except KeyError:
        # random deterministic color
        import hashlib
        color = '#' + hashlib.sha1(obj.encode()).hexdigest()[-6:]
    return color
