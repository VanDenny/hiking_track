import gpxpy
from Clawer_Base.shape_io import Shapefile_Write
from Clawer_Base.db_io import get_filepath
import os
import pandas as pd


def gps2shp(file_path, df):
    file_name = os.path.split(file_path)[1]
    record_df = df[df['filename'] == file_name]
    record_dict = record_df.to_dict('record')[0]
    gpx_file = open(file_path, 'r')
    gpx = gpxpy.parse(gpx_file)
    point_w = Shapefile_Write('point', [["Time", "C"]])
    line_w = Shapefile_Write(
            'line',
            [["trackId", "C"], ["name", "C"], ["type", "C"], ["distination", "C"], ["initial", "C"],
             ["date", 'C'], ["user", "C"], ['filename', "C"], ["start_time", "C"], ["end_time", "C"],
             ["collect", "N"], ["download", "N"], ["like", "N"], ["pic_num", "N"], ["distance", "N", 8, 2],
             ["moving_time", "N", 8, 0], ["stopped_time", "N", 8, 0], ['moving_distance', "N", 8, 2],
             ["stopped_distance", "N", 8, 2], ["max_speed", "N", 8, 2], ['duration', "N", 8, 2],
             ["uphill", "N", 8, 2], ["downhill", "N", 8, 2]
             ])
    mv = gpx.get_moving_data()
    updown = gpx.get_uphill_downhill()
    timebound = gpx.get_time_bounds()
    line_property = [
        record_dict["trackId"],
        record_dict["name"],
        record_dict["type"],
        record_dict["distination"],
        record_dict["initial"],
        record_dict["user"],
        record_dict["date"],
        record_dict["filename"],
        timebound.start_time,
        timebound.end_time,
        record_dict["collect"],
        record_dict["download"],
        record_dict["like"],
        record_dict["pic_num"],
        record_dict["distance"],
        mv.moving_time, mv.stopped_time, mv.moving_distance, mv.stopped_distance,
        mv.max_speed, gpx.get_duration(), updown.uphill, updown.downhill
    ]
    point_list = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                point_geo = [point.longitude, point.latitude, point.elevation, 0]
                # sw.plot(point_geo, (point.time.strftime("%Y%m%d%H%M%S")))
                point_list.append(point_geo)
                point_w.plot(point_geo, (point.time,))
    path_parts = os.path.splitext(file_path)
    point_w.save(path_parts[0]+'_pt')
    line_w.plot(point_list, tuple(line_property))
    line_w.save(path_parts[0]+'_ln')

if __name__ == "__main__":
    file_paths = get_filepath(r'D:\program_lib\hiking_track\result\GPX')
    for file_path in file_paths:
        if '.gpx' in file_path:
            print(file_path)
            record_df = pd.read_excel(r'D:\program_lib\hiking_track\result\威海.xlsx')
            gps2shp(file_path, record_df)
    # record_df = pd.read_excel(r'D:\program_lib\hiking_track\result\威海.xlsx')
    # print(record_df[record_df['filename'] == 'WH_1.gpx'].loc[0, 'collect'])
    # record_dict = record_df[record_df['filename'] == 'WH_1.gpx'].to_dict('record')[0]
    # print(record_dict)