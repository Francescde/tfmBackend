--SELECT id, nodes, tags FROM public.planet_osm_ways;

CREATE OR REPLACE FUNCTION public.update_node_way()
RETURNS NUMERIC AS $value$
DECLARE
   i integer;
   ret numeric;
   temprow record;
   node bigint;
   is_limit bool;
   id_way bigint;
BEGIN
  DO $$
    BEGIN
        BEGIN
            ALTER TABLE planet_osm_nodes ADD COLUMN height numeric(15,5);
        EXCEPTION
            WHEN duplicate_column THEN RAISE NOTICE 'column height already exists in <table_name>.';
     END;
  END$$;

	--eliminem taules anteriors
  DROP VIEW IF EXISTS final_nodes;
  DROP VIEW IF EXISTS all_nodes_geo_view;
  DROP VIEW IF EXISTS all_nodes;
  DROP TABLE IF EXISTS Way_Point;
  DROP TABLE IF EXISTS Way_Relation;
  --creem tamules
  Create table Way_Point (
		id_way bigint,
		id_node bigint,
		way_position int,
		is_limit bool,
		id_from bigint,
		dist_from numeric(15,5),
		ramp_neg_from numeric(15,5),
		ramp_pos_from numeric(15,5),
		id_to bigint,
		dist_to numeric(15,5),
		ramp_neg_to numeric(15,5),
		ramp_pos_to numeric(15,5),
      PRIMARY KEY(id_way, id_node, way_position));
  Create table Way_Relation (
	  id_way bigint,
	  id_self_key bigint PRIMARY KEY,
      dist numeric(15,5),
      ramp_neg numeric(15,5),
      ramp_pos numeric(15,5),
      oneway smallint,
      highway_type varchar(50));
  Raise Notice 'taules creades';
  --generar inserts
  id_way := 1;
  FOR temprow IN
  SELECT id, nodes, tags
	FROM public.planet_osm_ways
	where 'highway' = ANY(tags)
		and ('path'= ANY(tags) OR 'motorway'= ANY(tags) OR'trunk'= ANY(tags) OR
			 'primary'= ANY(tags) OR 'secondary'= ANY(tags) OR 'tertiary'= ANY(tags) OR
			 'unclassified'= ANY(tags) OR 'residential'= ANY(tags) OR 'motorway_link'= ANY(tags) OR
			 'trunk_link'= ANY(tags) OR 'primary_link'= ANY(tags) OR 'secondary_link'= ANY(tags) OR
			 'tertiary_link'= ANY(tags) OR 'living_street'= ANY(tags) OR 'service'= ANY(tags) OR
			 'pedestrian'= ANY(tags) OR 'track'= ANY(tags) OR 'road'= ANY(tags) OR
			 'footway'= ANY(tags) OR 'steps'= ANY(tags) OR 'path'= ANY(tags))
		and not 'abandoned:highway' = any(tags)
  LOOP
	--INSERT INTO user_data.leaderboards (season_num,player_id,season_pts) VALUES (old_seasonnum,temprow.userd_id,temprow.season_ptss);
	if not ('path'= ANY(temprow.tags) OR 'footway'= ANY(temprow.tags) or 'pedestrian'= ANY(temprow.tags))
	then
		i:=1;
		INSERT INTO public.Way_Relation values (temprow.id,id_way,NULL,NULL,NULL,NULL,NULL);
		FOREACH node IN ARRAY temprow.nodes
		LOOP
		  is_limit := (i = 1) or (i = array_length(temprow.nodes,1));
		  INSERT INTO public.Way_Point values (id_way,node,i,is_limit);
		  i:=i+1;
		END LOOP;
		id_way := id_way + 1;
	end if;
	if ('path'= ANY(temprow.tags) OR 'footway'= ANY(temprow.tags) or 'pedestrian'= ANY(temprow.tags))
		and exists(select osmn.id
    				FROM public.planet_osm_nodes osmn
					where osmn.lat<416400580 and osmn.lat>415423130
				    and osmn.lon>17478543 and osmn.lon<18759633 and osmn.id =any(temprow.nodes))
	then
		i:=1;
		INSERT INTO public.Way_Relation values (temprow.id,id_way,NULL,NULL,NULL,NULL,NULL);
		FOREACH node IN ARRAY temprow.nodes
		LOOP
		  is_limit := (i = 1) or (i = array_length(temprow.nodes,1));
		  INSERT INTO public.Way_Point values (id_way,node,i,is_limit);
		  i:=i+1;
		END LOOP;
		id_way := id_way + 1;
	end if;
  END LOOP;
  Raise Notice 'inserts generats %',id_way;
  -- posar com limits punts de tall
  ret:=0;
  RETURN ret;
END; $value$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION public.realitza_talls()
RETURNS NUMERIC AS $value$
DECLARE
   i integer;
   ret numeric;
   temprow record;
   actway bigint;
   maxkey bigint;
   actrow record;
   node bigint;
   is_limit bool;
   id_way bigint;
BEGIN
  UPDATE way_point
		SET is_limit = True
		WHERE  id_node in (select f.id_node
			from (SELECT *
			FROM public.way_point li
			where li.is_limit is False) f,(SELECT *
			FROM public.way_point li2
			where li2.is_limit is True) t
			where f.id_node=t.id_node);
  --generar inserts
  id_way := (select max(id_self_key) from Way_Relation)+1;

  Raise Notice 'tall preperat from %',id_way;
  FOR temprow IN
  SELECT *
    FROM public.way_point ori, Way_Relation owr
    where ori.is_limit is True and ori.way_position!=1 and exists (SELECT *
        FROM public.way_point n
        where  ori.id_way =n.id_way and ori.way_position+1=n.way_position)
	and owr.id_self_key = ori.id_way
  LOOP
	--INSERT INTO user_data.leaderboards (season_num,player_id,season_pts) VALUES (old_seasonnum,temprow.userd_id,temprow.season_ptss);
	i:=1;
	actway := (select k.id_way from Way_Relation k where k.id_self_key=temprow.id_way);
	INSERT INTO public.Way_Relation values (actway,id_way,NULL,NULL,NULL,NULL,NULL);
	actrow := temprow;
	maxkey := (SELECT min(wp.way_position)
		from public.way_point wp
		where actrow.way_position<wp.way_position and
		actrow.id_way =wp.id_way and wp.is_limit);
	FOR actrow IN
	  SELECT *
        FROM public.way_point n
        where  actrow.id_way =n.id_way
			and n.way_position<=maxkey
			and actrow.way_position<=n.way_position
		ORDER BY n.way_position ASC
	LOOP
	  INSERT INTO public.Way_Point values (id_way,actrow.id_node,i,actrow.is_limit);
	  i:=i+1;
	END LOOP;
	id_way := id_way + 1;
  END LOOP;
  Raise Notice 'talls fets %', id_way;
  -- posar com limits punts de tall
  delete from public.way_point n where Exists(select * from public.way_point n1 where n1.is_limit and n1.id_way =n.id_way and n.way_position>n1.way_position and n1.way_position!=1);
  ret:=0;
  Raise Notice 'talls fets';
  RETURN ret;
END; $value$
LANGUAGE plpgsql;


select public.update_node_way();
select public.realitza_talls();

CREATE OR REPLACE FUNCTION public.coe_update_node_way()
RETURNS NUMERIC AS $value$
DECLARE
   i integer;
   ret numeric;
   temprow record;
   node bigint;
   is_limit bool;
   id_way bigint;
BEGIN
  DO $$
    BEGIN
        BEGIN
            ALTER TABLE coe_nodes ADD COLUMN height numeric(15,5);
        EXCEPTION
            WHEN duplicate_column THEN RAISE NOTICE 'column height already exists in <table_name>.';
     END;
  END$$;

	--eliminem taules anteriors

  DROP VIEW IF EXISTS coe_final_nodes;
  DROP VIEW IF EXISTS coe_all_nodes;
  DROP VIEW IF EXISTS coe_all_nodes_geo_view;
  DROP TABLE IF EXISTS coe_Way_Point;
  DROP TABLE IF EXISTS coe_Way_Relation;
  --creem tamules
  Create table coe_Way_Point (
	  id_way bigint,
	  id_node bigint,
	  way_position int,
	  is_limit bool,
      id_from bigint,
      dist_from numeric(15,5),
      ramp_neg_from numeric(15,5),
      ramp_pos_from numeric(15,5),
      id_to bigint,
      dist_to numeric(15,5),
      ramp_neg_to numeric(15,5),
      ramp_pos_to numeric(15,5),
      PRIMARY KEY(id_way, id_node, way_position));
  Create table coe_Way_Relation (
	  id_way bigint,
	  id_self_key bigint PRIMARY KEY,
      dist numeric(15,5),
      ramp_neg numeric(15,5),
      ramp_pos numeric(15,5),
      oneway smallint,
      highway_type varchar(50));
  Raise Notice 'taules creades';
  --generar inserts
  id_way := 1;
  FOR temprow IN
  SELECT id, nodes, tags
	FROM public.coe_ways
	where 'highway' = ANY(tags)
		and ('path'= ANY(tags) OR 'motorway'= ANY(tags) OR'trunk'= ANY(tags) OR
			 'primary'= ANY(tags) OR 'secondary'= ANY(tags) OR 'tertiary'= ANY(tags) OR
			 'unclassified'= ANY(tags) OR 'residential'= ANY(tags) OR 'motorway_link'= ANY(tags) OR
			 'trunk_link'= ANY(tags) OR 'primary_link'= ANY(tags) OR 'secondary_link'= ANY(tags) OR
			 'tertiary_link'= ANY(tags) OR 'living_street'= ANY(tags) OR 'service'= ANY(tags) OR
			 'pedestrian'= ANY(tags) OR 'track'= ANY(tags) OR 'road'= ANY(tags) OR
			 'footway'= ANY(tags) OR 'steps'= ANY(tags) OR 'path'= ANY(tags))
		and not 'abandoned:highway' = any(tags)
  LOOP
	--INSERT INTO user_data.leaderboards (season_num,player_id,season_pts) VALUES (old_seasonnum,temprow.userd_id,temprow.season_ptss);
	if not ('path'= ANY(temprow.tags) OR 'footway'= ANY(temprow.tags) or 'pedestrian'= ANY(temprow.tags))
	then
		i:=1;
		INSERT INTO public.coe_Way_Relation values (temprow.id,id_way,NULL,NULL,NULL,NULL,NULL);
		FOREACH node IN ARRAY temprow.nodes
		LOOP
		  is_limit := (i = 1) or (i = array_length(temprow.nodes,1));
		  INSERT INTO public.coe_Way_Point values (id_way,node,i,is_limit);
		  i:=i+1;
		END LOOP;
		id_way := id_way + 1;
	end if;
	if ('path'= ANY(temprow.tags) OR 'footway'= ANY(temprow.tags) or 'pedestrian'= ANY(temprow.tags))
		and exists(select osmn.id
    				FROM public.coe_nodes osmn
					where osmn.lat<416400580 and osmn.lat>415423130
				    and osmn.lon>17478543 and osmn.lon<18759633 and osmn.id =any(temprow.nodes))
	then
		i:=1;
		INSERT INTO public.coe_Way_Relation values (temprow.id,id_way,NULL,NULL,NULL,NULL,NULL);
		FOREACH node IN ARRAY temprow.nodes
		LOOP
		  is_limit := (i = 1) or (i = array_length(temprow.nodes,1));
		  INSERT INTO public.coe_Way_Point values (id_way,node,i,is_limit);
		  i:=i+1;
		END LOOP;
		id_way := id_way + 1;
	end if;
  END LOOP;
  Raise Notice 'inserts generats %',id_way;
  -- posar com limits punts de tall
  ret:=0;
  RETURN ret;
END; $value$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION public.coe_realitza_talls()
RETURNS NUMERIC AS $value$
DECLARE
   i integer;
   ret numeric;
   temprow record;
   actway bigint;
   maxkey bigint;
   actrow record;
   node bigint;
   is_limit bool;
   id_way bigint;
BEGIN
  UPDATE coe_way_point
		SET is_limit = True
		WHERE  id_node in (select f.id_node
			from (SELECT *
			FROM public.coe_way_point li
			where li.is_limit is False) f,(SELECT *
			FROM public.coe_way_point li2
			where li2.is_limit is True) t
			where f.id_node=t.id_node);
  --generar inserts
  id_way := (select max(id_self_key) from coe_Way_Relation)+1;

  Raise Notice 'tall preperat from %',id_way;
  FOR temprow IN
  SELECT *
    FROM public.coe_way_point ori, coe_Way_Relation owr
    where ori.is_limit is True and ori.way_position!=1 and exists (SELECT *
        FROM public.coe_way_point n
        where  ori.id_way =n.id_way and ori.way_position+1=n.way_position)
	and owr.id_self_key = ori.id_way
  LOOP
	--INSERT INTO user_data.leaderboards (season_num,player_id,season_pts) VALUES (old_seasonnum,temprow.userd_id,temprow.season_ptss);
	i:=1;
	actway := (select k.id_way from coe_Way_Relation k where k.id_self_key=temprow.id_way);
	INSERT INTO public.coe_Way_Relation values (actway,id_way,NULL,NULL,NULL,NULL,NULL);
	actrow := temprow;
	maxkey := (SELECT min(wp.way_position)
		from public.coe_way_point wp
		where actrow.way_position<wp.way_position and
		actrow.id_way =wp.id_way and wp.is_limit);
	FOR actrow IN
	  SELECT *
        FROM public.coe_way_point n
        where  actrow.id_way =n.id_way
			and n.way_position<=maxkey
			and actrow.way_position<=n.way_position
		ORDER BY n.way_position ASC
	LOOP
	  INSERT INTO public.coe_Way_Point values (id_way,actrow.id_node,i,actrow.is_limit);
	  i:=i+1;
	END LOOP;
	id_way := id_way + 1;
  END LOOP;
  Raise Notice 'talls fets %', id_way;
  -- posar com limits punts de tall
  delete from public.coe_way_point n where Exists(select * from public.coe_way_point n1 where n1.is_limit and n1.id_way =n.id_way and n.way_position>n1.way_position and n1.way_position!=1);
  ret:=0;
  Raise Notice 'talls fets';
  RETURN ret;
END; $value$
LANGUAGE plpgsql;


select public.coe_update_node_way();
select public.coe_realitza_talls();

CREATE OR REPLACE FUNCTION public.inicialize_point_relatedTables()
RETURNS NUMERIC AS $value$
DECLARE
BEGIN

  create or replace view final_nodes as select osmp.id as id,
    (ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
    from public.way_point wp, public.planet_osm_nodes osmp
    where is_limit is true and id_node=osmp.id;

  create or replace view all_nodes as select osmp.id as id,
    (ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
    from public.way_point wp,public.planet_osm_nodes osmp
    where wp.id_node=osmp.id;

CREATE OR REPLACE VIEW public.all_nodes_geo_view AS
 SELECT osmp.id,
    st_setsrid(st_makepoint(osmp.lon::double precision / 10000000::double precision, osmp.lat::double precision / 10000000::double precision), 4326) AS geom,
    wp.id_to,
    wp.id_from,
    wp.dist_to,
    wp.dist_from
   FROM way_point wp,
    planet_osm_nodes osmp
  WHERE wp.id_node = osmp.id;

ALTER TABLE public.all_nodes_geo_view
    OWNER TO postgres;


Drop table IF EXISTS all_nodes_geometry;
CREATE TABLE public.all_nodes_geometry
(
    id bigint,
    geom geometry,
    id_to bigint,
    id_from bigint,
    dist_to numeric(15,5),
    dist_from numeric(15,5)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.all_nodes_geometry
    OWNER to postgres;


CREATE INDEX all_nodes_geometry_gix
    ON public.all_nodes_geometry USING gist
    (geom)
    TABLESPACE pg_default;
---------------------------

CREATE OR REPLACE VIEW public.coe_all_nodes_geo_view AS
 SELECT osmp.id,
    st_setsrid(st_makepoint(osmp.lon::double precision / 10000000::double precision, osmp.lat::double precision / 10000000::double precision), 4326) AS geom,
    wp.id_to,
    wp.id_from,
    wp.dist_to,
    wp.dist_from
   FROM coe_way_point wp,
    coe_nodes osmp
  WHERE wp.id_node = osmp.id;

ALTER TABLE public.coe_all_nodes_geo_view
    OWNER TO postgres;


Drop table IF EXISTS coe_all_nodes_geometry;
CREATE TABLE public.coe_all_nodes_geometry
(
    id bigint,
    geom geometry,
    id_to bigint,
    id_from bigint,
    dist_to numeric(15,5),
    dist_from numeric(15,5)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.coe_all_nodes_geometry
    OWNER to postgres;


CREATE INDEX coe_all_nodes_geometry_gix
    ON public.coe_all_nodes_geometry USING gist
    (geom)
    TABLESPACE pg_default;
--------------------------



  Drop table IF EXISTS temp_vehiclePositions;
  Create table temp_vehiclePositions (
      id_v int,
      geom geometry);

  Drop table IF EXISTS graph_nodes_geometry;
  Create table graph_nodes_geometry (
      id bigint,
      geom geometry);
  CREATE INDEX graph_nodes_geometry_gix ON graph_nodes_geometry USING GIST (geom);

  insert into graph_nodes_geometry(id, geom)
  select * from final_nodes
  GROUP BY id, geom;


  create or replace view coe_final_nodes as select osmp.id as id,
    (ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
    from public.coe_way_point wp, public.coe_nodes osmp
    where is_limit is true and id_node=osmp.id;

  create or replace view coe_all_nodes as select osmp.id as id,
    (ST_SetSRID(ST_MakePoint(CAST(osmp.lon AS FLOAT)/10000000, CAST(osmp.lat AS FLOAT)/10000000),4326)) as geom
    from public.coe_way_point wp,public.coe_nodes osmp
    where wp.id_node=osmp.id;
  RETURN 1;
END; $value$
LANGUAGE plpgsql;


select public.inicialize_point_relatedTables();

--fusiona

--select COUNT(id_node) from public.way_point where is_limit  group by id_node ORDER BY COUNT(id_node) DESC;

--select * from public.way_point where id_way=(select max(id_way) from public.way_point) order by way_position;

