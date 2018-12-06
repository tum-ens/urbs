import collections
import sys
import glob
import os

import pandas as pd
import urbs as urbs

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

""" Changes:

    Comments/DocStrings were added,removed or changed
        Fixed some word choices
        Added full text doc for some functions
    Capital letters for configuration (because 'constant' and 'final')
    Added exception to some try-except blocks
    removed LABEL={}
    Added to configuration:
        - extra width space for subplots
"""
# default settings
CONFIG = {'COMP_NAME_OUT': 'comparison',
          'FILTER': ['t', 'sit'],
          'KEEP_ZERO': False,
          'KEEP_SMALL_VALUES': False,
          'RESULT_FILE_PATTERN': 'scenario_*.h5',
          'SUBPLOTS': ['costs',
                       'e_pro_out',
                       'cap_tra_new',
                       'cap_pro_new']}


# predefined text with units for specific subgroups
PLOT_LABEL = {'costs': 'Total costs (EUR/a)',
              'e_pro_out': 'Total energy produced (MWh) / Emitted CO2 (t)'}

              
def dec_name(value):
    # short function to translate numbers (to the power of 10)
    # into their names
    alias = {1e3: 'thousand',
             1e6: 'million',
             1e9: 'billion',
             1e12: 'trillion',
             1e15: 'quadrillion'}
    try:
        return alias[value]
    except KeyError:
        return value


def gen_text(decimal_dict):
    """ Creates x label for plot.

    Args:
        decimal_dict: dict with groups as key and decimal dimension as values

    Return:
        dictionary with groups as key as text as value.
    """
    _temp = decimal_dict
    text = {}
    for key in _temp:
        try:
            text[key] = PLOT_LABEL[key]
        except KeyError:
            text[key] = key.replace('_', ' ')
        text[key] += f"\nin {dec_name(_temp[key])}s"
    return text


def get_most_recent(search_dir):
    """ Return most recently modified entry from given directory.

    Args:
        search_dir: absolute or relative path to a directory

    Returns:
        The file/folder in search_dir that has the most recent 'modified'
        datetime.
    """
    entries = glob.glob(os.path.join(search_dir, "*"))
    entries.sort(key=lambda x: os.path.getmtime(x))
    return entries[-1]


def get_result_files(folder_dir):
    """ Returns list of result files which are to be compared.

    Args:
        folder_dir: absolute or relative path to folder containing the files

    Returns:
        List of files (paths), located in the folder_dir,
        that match the result_file_pattern (CONFIG).
    """
    pattern = os.path.join(folder_dir, CONFIG['RESULT_FILE_PATTERN'])
    return glob.glob(pattern)


def summarize(dataframe, key='default'):
    """ Summarizes a key for a given dataframe;returns compact result.

    Summarizes a key for a given dataframe;returns compact result.
    If dataframe does not contain given key, original dataframe
    will be returned.
    Function cleans up irrelevant indices of dataframe depending on
    needs.
    e.g. - Data of single timesteps are irrelevant for actual long-term
           comparisons; summarize bigger timeframe
         - Locations may be summarized when comparing larger regions

    Args:
        dataframe:  dataframe
        key:        key or index to summarize

    Returns:
        Processed or original dataframe.
    """
    if key == 'default':
        df = dataframe
        for item in CONFIG['FILTER']:
            df = summarize(df, item)
        return df

    if key in dataframe.index.names:  # does it exist?
        levels = len(dataframe.index.names)  # unstack()-able levels
        indexNames = dataframe.index.names
        attempt = 0
        new = dataframe
        try:
            while key in indexNames and attempt < levels:
                new = dataframe.unstack(attempt)
                attempt += 1
                indexNames = new.index.names
        except:
            pass
        return new.sum(axis=1)
    return dataframe


def remove_zero(dataframe, cut=0.001, keep=CONFIG['KEEP_SMALL_VALUES']):
    """ Removes zero rows and columns. Optional: Also removes small values.

    Plotting data with a lot of zero bars convolutes the diagram.
    This removes lesser values to improve readability.
    When compared to very large numbers, small values are similar
    to actual zero values.

    Args:
        dataframe:  dataframe
        cut:        threshold
        keep:       Keep small values

    Returns:
        Dataframe without zero columns/rows (or small values)
    """
    if not keep:
        dataframe[abs(dataframe) < (dataframe.max().max()*cut)] = 0
    if isinstance(dataframe, pd.core.series.Series):
        dataframe = dataframe[(dataframe != 0)]
        return dataframe
    dataframe = dataframe[(dataframe.T != 0).any()].T
    dataframe = dataframe[(dataframe.T != 0).any()]
    return dataframe.T


def compare_scenarios(result_files, output_name):
    """ Compares result files of different scenarios.
    
    Args:
        result_files: list with paths to result files
        output_name: filename for comparison results
        
    Returns:
        Nothing
    """
    scenario_names = [os.path.basename(rf)  # drop folder names, keep filename
                      .replace('scenario_', '')  # drop 'scenario_' prefix
                      .replace('.h5', '')  # drop file extension
                      .replace('_', ' ')  # replace _ with spaces
                      for rf in result_files]

    scenarios = collections.OrderedDict()
    buffer = collections.OrderedDict()

    # loads scenario h5 files into dictionary for easier handling
    for rsf, name in zip(result_files, scenario_names):
        buffer[name] = urbs.load(rsf)

    # sorts scenario dict in descending order with 'base' scenario at the end
    order = list(buffer.keys())
    order.sort()
    if 'base' in order:
        order.insert(0, order.pop(order.index('base')))
    order.reverse()
    for i in order:
        scenarios[i] = buffer[i]

    totalsum = {}
    decimal = {}
    colors = {}

    for group in CONFIG['SUBPLOTS']:
        totalsum[group] = pd.DataFrame()
        # summarize, clean up, merge
        for key in scenarios:
            single = scenarios[key]._result[group]
            single = summarize(single)
            single = remove_zero(single, keep=True)
            single = pd.DataFrame(single)
            single.columns = [key]
            totalsum[group] = pd.concat([totalsum[group], single], axis=1,
                                        sort=True)
        if len(totalsum[group].index.names) > 1:
            totalsum[group] = totalsum[group].unstack()
        totalsum[group] = totalsum[group].T

        # thousands
        shf = 0
        while totalsum[group].max().max() > 10**(shf+4):
            shf += 3
        totalsum[group] /= (10**shf)
        decimal[group] = (10**shf)

        # colors
        try:
            colors[group] = [urbs.to_color(com) for com in totalsum[group]]
        except:
            pass

    # PLOTTING
    num = len(CONFIG['SUBPLOTS'])  # number of subplots
    height = int(num**0.5)
    width = int(num/height)+num % height
    figure, axes = plt.subplots(nrows=height, ncols=width, figsize=(7*width,
                                7*height), dpi=250, tight_layout={'pad': 3})
    plot = [None]*num

    if height == 1:
        for num, group in enumerate(CONFIG['SUBPLOTS']):
            plot[num] = totalsum[group].plot.barh(stacked=True, ax=axes[num],
                                                color=colors[group])
        figure.subplots_adjust(wspace=.0)

    else:
        key = list(totalsum.keys())
        count = 0
        for row in range(height):
            for col in range(width):
                try:
                    plot[count] = totalsum[key[count]].plot.barh(stacked=True,
                                                                 ax=axes[row][col],
                                                                 color=colors[key[count]])
                    count += 1
                except:
                    figure.delaxes(axes[row][col])
        figure.subplots_adjust(hspace=.250, wspace=.0)

    # Labeling
    plot_text = gen_text(decimal)
    first = True
    for subplot, group in zip(plot, CONFIG['SUBPLOTS']):
        subplot.set_xlabel(plot_text[group])
        if not first:
            try:
                subplot.set_yticklabels(totalsum[group].index
                                        .get_level_values(1))
            except:
                pass
        first = False

    # Format/Legend
    # To Do: Change the following for better readability
        subplot.set_ylabel('')
        plt.setp(list(subplot.spines.values()), color=urbs.to_color('Grid'))
        subplot.yaxis.grid(False)
        subplot.xaxis.grid(True, 'major', color=urbs.to_color('Grid'),
                           linestyle='-')
        subplot.xaxis.set_ticks_position('none')
        subplot.yaxis.set_ticks_position('none')

        # 1,000,000
        group_thousands = tkr.FuncFormatter(lambda x,
                                            pos: '{:0,d}'.format(int(x)))
        subplot.xaxis.set_major_formatter(group_thousands)

        # legend
        lg = subplot.legend(frameon=False, loc='upper center',
                            ncol=5, bbox_to_anchor=(0.5, 1.1),
                            fontsize='small')
        plt.setp(lg.get_patches(), edgecolor=urbs.to_color('Decoration'),
                 linewidth=0)

    # save files for each extension/file type
    fullname = f"{output_name}_{len(CONFIG['SUBPLOTS'])}p"
    for ext in ['png', 'pdf']:
        plt.gcf().savefig(f"{fullname}.{ext}")
        print(f"File saved: {fullname}.{ext}",)

if __name__ == '__main__':
    directories = sys.argv[1:]

    # defaults to this option if no paths were given
    if not directories:
        directories = [get_most_recent('result')]

    for path in directories:
        result_files = get_result_files(path)
        filename = os.path.join(path, CONFIG['COMP_NAME_OUT'])
        compare_scenarios(list(result_files), filename)