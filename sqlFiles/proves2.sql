SELECT id_way, id_node, way_position, is_limit
	FROM public.way_point;


drop table graph_nodes_geometry;
Create table graph_nodes_geometry (
	  id bigint primary key,
	  geom geometry);


drop table predecesorList;
select distinct(finalNode) from predecesorList;

Select finalNode, fromNode, toNode from predecesorList where finalNode=toNode
order by finalNode;

CREATE INDEX BTreeOnPredecesorList ON predecesorList USING btree (finalNode, vehicle, fromNode);
CREATE INDEX BTreeOnPredecesorList2 ON predecesorList USING btree (finalNode, vehicle, toNode);

WITH RECURSIVE pops (fromNode, level, finalNode, vehicle, node_path) AS (
    SELECT  fromNode, 0, finalNode, vehicle, ARRAY[toNode]
    FROM    predecesorList
    WHERE   toNode = 1909600474 and finalNode=1909600474 and vehicle=2
    UNION ALL
    SELECT  p.fromNode, t0.level + 1, p.finalNode, p.vehicle, ARRAY_APPEND(t0.node_path, p.fromNode)
    FROM    predecesorList p
    where finalNode=1909600474 and vehicle=2
    INNER JOIN pops t0 ON t0.fromNode = p.toNode
						and t0.finalNode=p.finalNode
						and t0.vehicle=p.vehicle
)
SELECT  fromNode, level,finalNode, vehicle, node_path
FROM  pops
where fromNode = 8670494 and finalNode=1909600474 and vehicle=2

WITH RECURSIVE routeSingle AS (
   SELECT finalNode, toNode, vehicle
   FROM
      predecesorList
   WHERE
      fromNode = 8670494 and finalNode=1909600474 and vehicle=2
   Union all
	Select n.finalNode, n.toNode, n.vehicle
	from
	 predecesorList n
  	INNER JOIN routeSingle mtree
	ON mtree.toNode = n.fromNode )
	select * from routeSingle;


WITH RECURSIVE routeSingle AS (
   SELECT finalNode, vehicle, toNode
   FROM
      predecesorList b
   WHERE
      fromNode = 8670494 and finalNode=1909600474 and vehicle=2
   Union all
	Select finalNode, vehicle, fromNode
	from
	 predecesorList n
	where finalNode=1909600474 and vehicle=2
) SELECT *
FROM
   routeSingle;

Drop table predecesorList;
Create table predecesorList (
	  finalNode bigint,
	  fromNode bigint,
	  toNode bigint,
	  vehicle smallint,
	  posRamp float,
	  negRamp float,
	  dist float,
	  costg float,
	  costWalk float,
	  costCar float,
	  costBrp float,
	  cost4x4 float,
	  primary key (finalNode, fromNode, vehicle));



create or replace view final_nodes as select osmp.id as id,
	(ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
	from public.way_point wp, public.planet_osm_nodes osmp
	where is_limit is true and id_node=osmp.id;

insert into graph_nodes_geometry(id, geom)
select * from final_nodes
group by id, geom;

CREATE INDEX graph_nodes_geometry_gix ON graph_nodes_geometry USING GIST (geom);
select count(*) from graph_nodes_geometry;

delete from graph_nodes_geometry;

select min(lat) from public.planet_osm_nodes;
select max(lat)-min(lat) from public.planet_osm_nodes;
select min(lon) from public.planet_osm_nodes;
select max(lon)-min(lon) from public.planet_osm_nodes;

select * from(
SELECT b.id, ve.id_v, ST_Distance(b.geom, ve.geom)
     FROM temp_vehiclePositions ve
     JOIN LATERAL( SELECT fi.id as id, fi.geom as geom
     FROM graph_nodes_geometry fi
     ORDER BY ve.geom <-> fi.geom
     LIMIT 1) AS b
     ON true) as d
where id_v=246488;

select *
        FROM public.graph_nodes_geometry osmn
           where osmn.id = 246488


SELECT b.id, ve.id_v, ST_Distance(b.geom,ve.geom)
FROM temp_vehiclePositions ve
JOIN LATERAL (
  SELECT fi.id as id, fi.geom as geom
  FROM graph_nodes_geometry fi
  ORDER BY ve.geom <-> fi.geom
  LIMIT 1
) AS b
ON true;

select min lat from

create or replace view final_nodes as select osmp.id as id,
	(ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
	from public.way_point wp, public.planet_osm_nodes osmp
	where is_limit is true and id_node=osmp.id;


----------
with recursive name_tree as (
   select fromNode, toNode, finalNode, vehicle
   from predecesorList
   where fromNode = 2278830907 and finalNode=1909600474 and vehicle=2
   union all
   select c.fromNode, c.toNode, c.finalNode, c.vehicle
   from predecesorList c
   join name_tree p ON p.toNode = c.fromNode
						and p.finalNode=c.finalNode
						and p.vehicle=c.vehicle  -- this is the recursion
)
select *
from name_tree;

select count(*) from predecesorList;


select fromNode, toNode, finalNode, vehicle
   from predecesorList
   where  finalNode=1909600474 and vehicle=2
delete from predecesorList;
WITH RECURSIVE pops (fromNode, level, finalNode, vehicle, node_path) AS (
    SELECT  fromNode, 0, finalNode, vehicle, ARRAY[toNode]
    FROM    predecesorList
    WHERE   toNode = finalNode
    UNION ALL
    SELECT  p.fromNode, t0.level + 1, p.finalNode, p.vehicle, ARRAY_APPEND(t0.node_path, p.fromNode)
    FROM predecesorList p
    INNER JOIN pops t0 ON t0.fromNode = p.toNode
						and t0.finalNode=p.finalNode
						and t0.vehicle=p.vehicle
)
SELECT  fromNode, level,finalNode, vehicle, node_path
FROM  pops




