#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt
import sys
import math
import os

# sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Figures/')
# sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/Figures/')
sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-07-17-2012/Figures/')
# sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Possible Storms/Storm 02-24-2016/Figures/')
# sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-25-2016/Figures')
# sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-03-26-2016/Figures')
# sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-04-02-2016/Figures')

import radar_entire_storm_ppi as entire
# import radar_start_to_first_flash as first


def entire_storm_ppi(file_ind=-5):
    for radar_file in entire.radar_files:
        print("Reading radar file: " + radar_file)

        # radar_plotter = df.RadarPlotter(radar_file, shift=[0, 0])
        try:
            radar_plotter = df.RadarPlotter(radar_file, EET=entire.EET)
        except FileNotFoundError:
            print("   *** No radar file for this time.")
            continue
        except NotImplementedError:
            print("   *** Corrupted file")
            continue

        # radar_plotter.filter_data()
        radar_plotter.setup_display()

        for field in entire.fields:
            print("  - Plotting {0}".format(field))
            fig, ax = plt.subplots(1, 1)
            radar_plotter.plot_ppi(field, fig=fig, ax=ax)
            ax.scatter(0, 0, s=50, c='w')
            ax.set_xlim([-50, 50])
            ax.set_ylim([-50, 50])
            ax.set_xlabel('West - East (km)')
            ax.set_ylabel('South - North (km)')
            ax.set_title(radar_file[2:])
            ax.minorticks_on()
            ax.grid(True, which='both')
            if file_ind is not None:
                save_file = entire.save_parent + radar_file[2:file_ind] + '_' + field + '_PPI.png'
            else:
                save_file = entire.save_parent + radar_file[2:] + '_' + field + '_PPI.png'
            fig.savefig(save_file, dpi=300, format='png')
            plt.close(fig)


def entire_storm_ppi_rhi(azimuth=205):
    for radar_file in entire.radar_files:
        print("Reading radar file: " + radar_file)

        radar_plotter = df.RadarPlotter(radar_file, shift=[0, 0])
        # radar_plotter = df.RadarPlotter(radar_file)

        radar_plotter.filter_data()
        radar_plotter.setup_display()

        for field in entire.fields:
            print("  - Plotting {0}".format(field))

            # Plot dual-pol data
            radar_plotter.plot_ppi_rhi(field=field, start_azimuth=azimuth)
            fig_rhi = radar_plotter._fig_rhi
            fig_ppi = radar_plotter._fig_ppi

            ax_rhi = radar_plotter._ax_rhi
            ax_ppi = radar_plotter._ax_ppi

            ax_ppi.set_xlim([radar_plotter.iclrt_x_y[0]*1e-3 - 20,
                             radar_plotter.iclrt_x_y[0]*1e-3 + 20])
            ax_ppi.set_ylim([radar_plotter.iclrt_x_y[1]*1e-3 - 20,
                             radar_plotter.iclrt_x_y[1]*1e-3 + 20])

            ax_ppi.set_title(radar_file[2:])
            ax_rhi.set_title(radar_file[2:])

            ax_ppi.set_xlabel('West - East (km)')
            ax_ppi.set_ylabel('South - North (km)')

            ax_rhi.set_xlabel('Distance from radar (km)')
            ax_rhi.set_ylabel('Altitude (km)')

            ax_rhi.set_xlim([radar_plotter._radius - 10, radar_plotter._radius + 10])
            ax_rhi.set_ylim([0, 12])

            save_file = entire.save_parent + radar_file[2:-7] + '_' + field + '_PPI.png'
            fig_ppi.savefig(save_file, dpi=300, format='png')
            plt.close(fig_ppi)

            save_file = entire.save_parent + radar_file[2:-7] + '_' + field + '_RHI.png'
            fig_rhi.savefig(save_file, dpi=300, format='png')
            plt.close(fig_rhi)


def start_to_first_flash_ppi(coord=None):
    coord_set = False

    for radar_file in first.radar_files:
        print("Reading radar file: " + radar_file)

        radar_plotter = df.RadarPlotter(radar_file, shift=[0, 0])
        # radar_plotter = df.RadarPlotter(radar_file)

        radar_plotter.filter_data()
        radar_plotter.setup_display()

        if not coord_set:
            if coord is not None:
                coord = (coord[0] + radar_plotter.iclrt_x_y[0],
                         coord[1] + radar_plotter.iclrt_x_y[1])
            else:
                coord = radar_plotter.iclrt_x_y

            coord_set = True

        for field in first.fields:
            print("  - Plotting {0}".format(field))
            fig, ax = plt.subplots(1, 1)
            radar_plotter.plot_ppi(field, fig=fig, ax=ax, start_coord=coord)
            ax.scatter(radar_plotter.iclrt_x_y[0]*1e-3,
                       radar_plotter.iclrt_x_y[1]*1e-3,
                       s=50, c='w')
            ax.set_xlim([radar_plotter.iclrt_x_y[0]*1e-3-40, radar_plotter.iclrt_x_y[0]*1e-3+40])
            ax.set_ylim([radar_plotter.iclrt_x_y[1]*1e-3-40, radar_plotter.iclrt_x_y[1]*1e-3+40])
            ax.set_xlabel('West - East (km)')
            ax.set_ylabel('South - North (km)')
            ax.set_title(radar_file[2:])
            save_file = first.save_parent + radar_file[2:-5] + '_' + field + '_PPI.png'
            fig.savefig(save_file, dpi=300, format='png')
            plt.close(fig)


def start_to_first_flash_ppi_rhi(azimuth=205, coord=None, file_ind=-7):
    coord_set = False
    flag = False

    if azimuth == None:
        flag = True

    for i, radar_file in enumerate(first.radar_files):
        print("Reading radar file: " + radar_file)

        if flag:
            azimuth = first.azimuths[i]

        radar_plotter = df.RadarPlotter(radar_file, shift=[0, 0])
        # radar_plotter = df.RadarPlotter(radar_file)

        radar_plotter.filter_data()
        radar_plotter.setup_display()

        if not coord_set:
            if coord is not None:
                try:
                    z = coord[2]
                    coord = (coord[0] + radar_plotter.iclrt_x_y[0],
                             coord[1] + radar_plotter.iclrt_x_y[1],
                             z)

                except:
                    coord = (coord[0] + radar_plotter.iclrt_x_y[0],
                             coord[1] + radar_plotter.iclrt_x_y[1])
            else:
                coord = radar_plotter.iclrt_x_y

            coord_set = True

        for field in first.fields:
            print("  - Plotting {0}".format(field))

            # Plot dual-pol data
            radar_plotter.plot_ppi_rhi(field=field, start_azimuth=azimuth,
                                       start_coord=coord)
            fig_rhi = radar_plotter._fig_rhi
            fig_ppi = radar_plotter._fig_ppi

            ax_rhi = radar_plotter._ax_rhi
            ax_ppi = radar_plotter._ax_ppi

            ax_ppi.set_xlim([coord[0]*1e-3 - 20,
                             coord[0]*1e-3 + 20])
            ax_ppi.set_ylim([coord[1]*1e-3 - 20,
                             coord[1]*1e-3 + 20])

            ax_ppi.set_title(radar_file[2:])
            ax_rhi.set_title(radar_file[2:])

            ax_ppi.set_xlabel('West - East (km)')
            ax_ppi.set_ylabel('South - North (km)')

            ax_rhi.set_xlabel('Distance from radar (km)')
            ax_rhi.set_ylabel('Altitude (km)')

            ax_rhi.set_xlim([radar_plotter._radius - 30, radar_plotter._radius + 30])
            ax_rhi.set_ylim([0, 15])

            xlims = ax_rhi.get_xlim()
            ax_rhi.plot([xlims[0], xlims[1]], [first.fzl, first.fzl],
                        ls='dotted', c='gray')  # plot FZL
            ax_rhi.plot([xlims[0], xlims[1]], [first.minus_10, first.minus_10],
                        ls='dotted', c='gray')  # plot FZL
            ax_rhi.plot([xlims[0], xlims[1]], [first.minus_20, first.minus_20],
                        ls='dotted', c='gray')  # plot FZL

            # plt.show()
            # continue

            save_file = first.save_parent + radar_file[2:file_ind] + '_' + field + '_PPI.png'
            fig_ppi.savefig(save_file, dpi=300, format='png')
            plt.close(fig_ppi)

            save_file = first.save_parent + radar_file[2:file_ind] + '_' + field + '_RHI.png'
            fig_rhi.savefig(save_file, dpi=300, format='png')
            plt.close(fig_rhi)


if __name__ == "__main__":
    # start_to_first_flash_ppi_rhi(first.azimuth, coord=first.flash_x_y_z,
    #                              file_ind=first.file_ind)
    # start_to_first_flash_ppi(coord=first.flash_x_y)
    entire_storm_ppi(entire.file_ind)

    # file = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 03-04-2016/Radar/KJAX/Level2_KJAX_20160304_0607.ar2v'
    # file = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 07-17-2012/Radar/KJAX/Level-II/KJAX20120717_200110_V06'
    # radar_plotter = df.RadarPlotter(file, shift=[0, 0])
    # radar_plotter.plot_ppi_rhi()
    # plt.show()
