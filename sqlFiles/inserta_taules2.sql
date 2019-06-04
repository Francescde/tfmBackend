--SELECT id, nodes, tags FROM public.planet_osm_ways;


Drop IF EXISTS table predecesorList;
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
CREATE INDEX BTreeOnPredecesorList ON predecesorList USING btree (finalNode, vehicle, fromNode);
CREATE INDEX BTreeOnPredecesorList2 ON predecesorList USING btree (finalNode, vehicle, toNode);
