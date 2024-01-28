# -*- coding: UTF-8 -*-
"""
@Project: MiTrace 
@File: analysis.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/1/26 15:22 
@Description:  Analysis the results from detection, maily a x_list and y_lst
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter


class Analysis:

    def __init__(self, x_lst=None, y_lst=None, video_adjust=None, roi_lst=None, roi_name_lst=None):
        """
        Analyze the results of detection, based on the x_lst and y_lst
        1. Result sheet
        2. Trace scatter plot
        3. Trace heatmap

        Parameters
        ----------
        x_lst : List
            x coordinates of object
        y_lst : List
            y coordinates of object
        video_adjust : List
            resize the video
        roi_lst : List
            A list of rois
        roi_name_lst : List
            A list of rois' name
        """

        if video_adjust is None:
            video_adjust = [1, 1, 10, 10]

        self.video_adjust = video_adjust
        self.x_lst = x_lst
        self.y_lst = y_lst
        self.roi_lst = roi_lst
        self.roi_name_lst = roi_name_lst
        self.video_adjust = video_adjust
        self.result_df = None
        self.roi_map = None

    def get_result_sheet(self):
        """
        Get the result sheet from x and y coordinates
        e.g.
        | frame | x_coordinate | y_coordinate | distance |
        |   1   |     383      |      27      |    0     |

        Returns
        -------
        result_df : DataFrame
            dataframe of x/y coordinates and distance
        """
        # result_df = pd.DataFrame(columns=['x_coordinate', 'y_coordinate', 'distance'])
        # result_df['x_coordinate'] = self.x_lst
        # result_df['y_coordinate'] = self.y_lst

        distance_lst = []
        for i in range(1, len(self.x_lst)):
            # Use Euclidean distance
            distance_lst.append(round(np.sqrt((self.y_lst[i] - self.y_lst[i - 1]) ** 2
                                              + (self.x_lst[i] - self.x_lst[i - 1]) ** 2), 4))

        # Pad a zero before distance_lst which is the first distance
        distance_lst = [0] + distance_lst

        # distance_lst = np.pad(np.array(distance_lst), (0, len(self.x_lst)-len(distance_lst)))
        # result_df['distance'] = distance_lst

        self.result_df = pd.DataFrame.from_dict({
            'frame': range(len(self.x_lst)),
            'x_coordinate': self.x_lst,
            'y_coordinate': self.y_lst,
            'distance': distance_lst
        }, orient='index').transpose()

    def analyze_roi(self):
        """
        Use the result sheet and the roi_lst to locate each roi's frame stamp
        The result sheet will be like
        | frame | x_coordinate | y_coordinate | distance |        roi       |
        |   0   |      383     |       27     |     0    | [20, 20, 10, 10] |

        and the roi field can be empty while there are some times the mouse is not
        in the roi area.

        Returns
        -------

        """

        self.result_df['roi'] = self.result_df.apply(self.roi_locate, axis=1)

        self.roi_map = pd.DataFrame(columns=['roi name', 'roi position'])
        self.roi_map['roi name'] = self.roi_name_lst
        self.roi_map['roi position'] = self.roi_lst

    def roi_locate(self, row):
        """
        Pass in a (x, y) coordinate, and determine the position is in the roi list or not.
        If 'yes' return the roi's name, if 'not' return empty

        Parameters
        ----------
        Row of self.result_df
        Returns
        -------

        """
        x = row['x_coordinate']
        y = row['y_coordinate']
        for idx, roi in enumerate(self.roi_lst):
            if roi[0] < x < roi[0]+roi[2] and roi[1] < y < roi[1] + roi[3]:
                return self.roi_name_lst[idx]

        return ''

    def get_trace_plot(self):
        """
        Plot the trace
        Returns
        -------
        fig : matplotlib.pyplot.Figure
            Figure contains trace plot
        """

        fig_trace, ax_trace = plt.subplots(nrows=1, ncols=1)
        ax_trace.set_aspect(1)  # Set the x and y coordinate bin equal
        ax_trace.set_xlim([0, self.video_adjust[2]])
        ax_trace.set_ylim([0, self.video_adjust[3]])
        ax_trace.plot(self.x_lst, self.y_lst, lw=1, c='k')
        # Move the ticks to the top
        ax_trace.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
        ax_trace.invert_yaxis()

        fig_heatmap, ax_heatmap = plt.subplots(nrows=1, ncols=1)
        heatmap, x_edge, y_edge = np.histogram2d(self.x_lst, self.y_lst,
                                                 bins=max(self.video_adjust[2], self.video_adjust[3]),
                                                 range=[[0, self.video_adjust[2]], [0, self.video_adjust[3]]])
        heatmap = gaussian_filter(heatmap, 6)
        heatmap = heatmap.T
        heatmap = heatmap[::-1, ]
        extent = [x_edge[0], x_edge[-1], y_edge[0], y_edge[-1]]
        # Move the ticks to the top
        ax_heatmap.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
        im = ax_heatmap.imshow(heatmap, cmap=plt.cm.jet, extent=extent)
        fig_heatmap.colorbar(im, ax=ax_heatmap)
        ax_heatmap.invert_yaxis()

        return fig_trace, fig_heatmap

    def save_results(self, folder_path):
        """
        Save results
        Returns
        -------

        """

        self.get_result_sheet()
        self.analyze_roi()
        fig_trace, fig_heatmap = self.get_trace_plot()

        with pd.ExcelWriter(f'{folder_path}/result.xlsx') as writer:
            self.result_df.to_excel(writer, sheet_name='trace_result', index=False)
            self.roi_map.to_excel(writer, sheet_name='roi_map', index=False)
        fig_trace.savefig(f'{folder_path}/trace_figure.pdf')
        fig_heatmap.savefig(f'{folder_path}/heatmap_figure.pdf')
