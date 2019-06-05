select * from public.planet_osm_nodes;

SELECT count(*)
	FROM public.way_point wp, public.planet_osm_nodes osmp
	where is_limit is true and id_node=osmp.id and ST_Distance(
		ST_SetSRID(ST_MakePoint(1.8210594, 41.5957756),4326),
		ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326))=(Select min(ST_Distance(
				ST_SetSRID(ST_MakePoint( 1.8210594, 41.5957756),4326),
				ST_SetSRID(ST_MakePoint(CAST(osmp2.lon AS FLOAT)/10000000, CAST(osmp2.lat AS FLOAT)/10000000),4326) ))
			FROM public.planet_osm_nodes osmp2);
select count(*) FROM public.way_point wp, public.planet_osm_nodes osmp where is_limit is true and id_node=osmp.id;
drop view all_nodes;
create or replace view final_nodes as select osmp.id as id,
	(ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
	from public.way_point wp, public.planet_osm_nodes osmp
	where is_limit is true and id_node=osmp.id;

create or replace view all_nodes as select osmp.id as id,
	(ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
	from public.way_point wp,public.planet_osm_nodes osmp
	where wp.id_node=osmp.id;

select * from final_nodes;

 Create table temp_vehiclePositions (
	  id_v int,
	  geom geometry);

SELECT b.id, ve.id_v, ST_Distance(b.geom,ve.geom)
FROM temp_vehiclePositions ve
JOIN LATERAL (
  SELECT fi.id as id, fi.geom as geom
  FROM final_nodes fi
  ORDER BY ve.geom <-> fi.geom
  LIMIT 1
) AS b
ON true;

select * from temp_vehiclePositions ve;

SELECT fi.id, ve.id_v, ST_Distance(fi.geom,ve.geom)
         FROM final_nodes fi, temp_vehiclePositions ve
         ORDER BY fi.geom <-> ve.geom
         LIMIT 1;



SELECT fi.id, ST_Distance(
		ST_SetSRID(ST_MakePoint(1.8210594,41.5957756),4326),
		fi.geomPoint) as dist
	FROM final_nodes fi
	order by dist ASC;

SELECT ST_AsKML(ST_SetSRID(ST_MakePoint(CAST(osmp2.lon AS FLOAT)/10000000, CAST(osmp2.lat AS FLOAT)/10000000),4326)) FROM public.planet_osm_nodes osmp2;




-------------------------------
SELECT id_way, id_node, way_position, is_limit
	FROM public.way_point;

Create table graph_nodes_geometry (
	  id bigint,
	  geom geometry);

insert into graph_nodes_geometry(id, geom)
select * from final_nodes;

SELECT fi.id, b.id_v, ST_Distance(b.geom,ve.geom)
FROM graph_nodes_geometry fi
JOIN LATERAL (
  SELECT ve.id_v as id_v, ve.geom as geom
  FROM temp_vehiclePositions ve
  ORDER BY ve.geom <-> fi.geom
  LIMIT 1
) AS b
ON true;


create or replace view final_nodes as select osmp.id as id,
	(ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
	from public.way_point wp, public.graph_nodes_geometry osmp
	where is_limit is true and id_node=osmp.id;