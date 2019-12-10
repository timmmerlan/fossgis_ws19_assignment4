#!/usr/bin/env python

import grass.script as gscript


def main():
    gscript.run_command('g.region', flags='p')
    
    #Adapt region to tarragona area
    gscript.run_command('g.region', vector='tarragona_region@PERMANENT')
    #Import raster files
    gscript.run_command('r.import', input='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/assignment4_data/assignment4_data/corine_landcover_2018/CLC2018_tarragona.tif', output='CLC2018_tarragona', overwrite=True)
    gscript.run_command('r.import', input='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/assignment4_data/assignment4_data/dem/N40E000.SRTMGL1.hgt.zip', output='N40E000', overwrite=True)
    gscript.run_command('r.import', input='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/assignment4_data/assignment4_data/dem/N41E000.SRTMGL1.hgt.zip', output='N41E000', overwrite=True)
    gscript.run_command('r.import', input='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/assignment4_data/assignment4_data/dem/N41E001.SRTMGL1.hgt.zip', output='N41E001', overwrite=True)
    #Import vector files
    gscript.run_command('v.import', input='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/assignment4_data/assignment4_data/fire_incidents/fire_archive_V1_89293.shp', output='fire_incidents', overwrite=True)
    gscript.run_command('v.import', input='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/assignment4_data/assignment4_data/osm/buildings.geojson', output='osm_buildings', overwrite=True)
    gscript.run_command('v.import', input='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/assignment4_data/assignment4_data/osm/fire_stations.geojson', output='osm_firestations', overwrite=True)
    gscript.run_command('r.patch', input='N40E000@PERMANENT,N41E000@PERMANENT,N41E001@PERMANENT', output='DEM', overwrite=True)
    #Calculate slope of DEM model
    gscript.run_command('r.slope.aspect', elevation='DEM@PERMANENT', slope='slope_DEM', overwrite=True, zscale="100.0")
    #Reclassify slope
    gscript.run_command('r.reclass', input='slope_DEM@PERMANENT', output='slope_DEM_reclassified', rules='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/reclassification_slope.txt', overwrite=True)
    gscript.run_command('r.resample', input='slope_DEM_reclassified@PERMANENT', output='slope_DEM_reclassified', overwrite=True)
    #Reclassify landuse raster
    gscript.run_command('r.reclass', input='CLC2018_tarragona@PERMANENT', output='CLC_2018_tarragona_reclassified', rules='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/reclassification_landcover.txt', overwrite=True)
    gscript.run_command('r.resample', input='CLC_2018_tarragona_reclassified@PERMANENT', output='CLC_2018_tarragona_reclassified', overwrite=True)

    #calculate fire probability
    #create grid for calculation
    gscript.run_command('v.mkgrid', map='fire_density', position='region', box='1000,1000', overwrite=True)
    #count fires per grid section
    gscript.run_command('v.vect.stats', points='fire_incidents@PERMANENT', areas='fire_density@PERMANENT', count_column='fire_count')
    #convert grid to raster with fire counter as raster value
    gscript.run_command('v.to.rast', input='fire_density@PERMANENT', output='fire_density_raster', use='attr', attribute_column='fire_count', overwrite=True, type='area')
    #calculate fire probability
    gscript.run_command('r.mapcalc', expression='fire_probability = (if( fire_density_raster@PERMANENT > 15, 15,  fire_density_raster@PERMANENT ) * 100 / 15)', overwrite=True)
    #reclassify fire probability
    gscript.run_command('r.reclass', input='fire_probability@PERMANENT', output='fire_probability_reclassified', rules='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/reclassification_fire_probability.txt', overwrite=True)
    gscript.run_command('r.resample', input='fire_probability_reclassified@PERMANENT', output='fire_probability_reclassified', overwrite=True)

    #calculate building density
    #create grid for calculation
    gscript.run_command('v.mkgrid', map='building_density', position='region', box='1000,1000', overwrite=True)
    #count buildings per grid section
    gscript.run_command('v.vect.stats', points='osm_buildings@PERMANENT', type='centroid', areas='building_density@PERMANENT', count_column='building_count')
    #convert grid to raster with building density as raster value
    gscript.run_command('v.to.rast', input='building_density@PERMANENT', output='building_density_raster', use='attr', attribute_column='building_count', overwrite=True, type='area')
    #reclassify building density
    gscript.run_command('r.reclass', input='building_density_raster@PERMANENT', output='building_density_reclassified', rules='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/reclassification_building_density.txt', overwrite=True)
    gscript.run_command('r.resample', input='building_density_reclassified@PERMANENT', output='building_density_reclassified', overwrite=True)

    #calculate distance to next fire station
    #create grid for calculation
    gscript.run_command('v.mkgrid', map='firestations_density', position='region', box='1000,1000', overwrite=True)
    #count firestations per grid
    gscript.run_command('v.vect.stats', points='osm_firestations@PERMANENT', areas='firestations_density@PERMANENT', count_column='firestation_count', type='point,centroid')
    #convert grid to raster with firestation counter as raster value
    gscript.run_command('v.to.rast', input='firestations_density@PERMANENT', output='firestations_raster', use='attr', overwrite=True,attribute_column='firestation_count')
    #set all 0 values of the raster to NULL --> only pixels with firestation are left
    gscript.run_command('r.null', map='firestations_raster@PERMANENT', setnull='0')
    #calculate distance to next firestation
    gscript.run_command('r.grow.distance', input='firestations_raster@PERMANENT', distance='firestations_distance', overwrite=True)
    #reclassify distance
    gscript.run_command('r.reclass', input='firestations_distance@PERMANENT', output='firestations_distance_reclassified', rules='D:/Dokumente_D/Uni/5_Semester/GIS_Proseminar/fossgis_ws19_assignment4/reclassification_fire_station_distance.txt', overwrite=True)
    gscript.run_command('r.resample', input='firestations_distance_reclassified@PERMANENT', output='firestations_distance_reclassified', overwrite=True)
if __name__ == '__main__':
    main()
