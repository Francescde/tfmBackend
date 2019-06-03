// C / C++ program for Dijkstra's shortest path algorithm for adjacency
// list representation of graph

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include<string.h>
#define MAX 468497

long long nodes[MAX];
int vehicles[MAX][3];
bool final[MAX];
int numNode=0;
int srcG=0;
int numFianls=0;

// A structure to represent a node in adjacency list
struct AdjListNode
{
    int dest;
    double walkingCost;
    double CarCost;
    double BRPCost;
    double AllTerrainCost;
    struct AdjListNode* next;
    double rampPos;
    double rampNeg;
    double dist;
};

struct PrecNodeDist
{
    int pred[4];
    double cost[4];
    bool final;
    AdjListNode* data[4];
};
PrecNodeDist pred[MAX];

// A structure to represent an adjacency liat
struct AdjList
{
    struct AdjListNode *head;  // pointer to head node of list
};


// A structure to represent a graph. A graph is an array of adjacency lists.
// Size of array will be V (number of vertices in graph)
struct Graph
{
    int V;
    struct AdjList* array;
};

// A utility function to create a new adjacency list node
struct AdjListNode* newAdjListNode(int dest, double walkingCost,double CarCost,double BRPCost,double AllTerrainCost,double rampPos, double rampNeg, double dist)
{
    struct AdjListNode* newNode =
            (struct AdjListNode*) malloc(sizeof(struct AdjListNode));
    newNode->dest = dest;
    newNode->walkingCost = walkingCost;
    newNode->CarCost = CarCost;
    newNode->BRPCost = BRPCost;
    newNode->AllTerrainCost = AllTerrainCost;
    newNode->rampPos=rampPos;
    newNode->rampNeg=rampNeg;
    newNode->dist=dist;
    newNode->next = NULL;
    return newNode;
}

// A utility function that creates a graph of V vertices
struct Graph* createGraph(int V)
{
    struct Graph* graph = (struct Graph*) malloc(sizeof(struct Graph));
    graph->V = V;

    // Create an array of adjacency lists.  Size of array will be V
    graph->array = (struct AdjList*) malloc(V * sizeof(struct AdjList));
    for (int i = 0; i < V; ++i){
        graph->array[i].head = NULL;
        nodes[i]=0;
        final[i]=false;
        vehicles[i][0]=vehicles[i][1]=vehicles[i][2]=0;
    }
    return graph;
}

// Adds an edge to an undirected graph
void addEdge(struct Graph* graph, int src, int dest, double walkingCost,double CarCost,double BRPCost,double AllTerrainCost,double rampPos, double rampNeg, double dist)
{
    srcG=src;
    // Add an edge from src to dest.  A new node is added to the adjacency
    // list of src.  The node is added at the begining
    struct AdjListNode* newNode = newAdjListNode(dest, walkingCost, CarCost, BRPCost, AllTerrainCost, rampPos,  rampNeg,  dist);
    newNode->next = graph->array[src].head;
    graph->array[src].head = newNode;

    // Since graph is undirected, add an edge from dest to src also
    /*
    newNode = newAdjListNode(src, weight);
    newNode->next = graph->array[dest].head;
    graph->array[dest].head = newNode;*/
}

// Structure to represent a min heap node
struct MinHeapNode
{
    int  v;
    double dist;
};

// Structure to represent a min heap
struct MinHeap
{
    int size;      // Number of heap nodes present currently
    int capacity;  // Capacity of min heap
    int *pos;     // This is needed for decreaseKey()
    struct MinHeapNode **array;
};

// A utility function to create a new Min Heap Node
struct MinHeapNode* newMinHeapNode(int v, double dist)
{
    struct MinHeapNode* minHeapNode =
           (struct MinHeapNode*) malloc(sizeof(struct MinHeapNode));
    minHeapNode->v = v;
    minHeapNode->dist = dist;
    return minHeapNode;
}

// A utility function to create a Min Heap
struct MinHeap* createMinHeap(int capacity)
{
    struct MinHeap* minHeap =
         (struct MinHeap*) malloc(sizeof(struct MinHeap));
    minHeap->pos = (int *)malloc(capacity * sizeof(int));
    minHeap->size = 0;
    minHeap->capacity = capacity;
    minHeap->array =
         (struct MinHeapNode**) malloc(capacity * sizeof(struct MinHeapNode*));
    return minHeap;
}

// A utility function to swap two nodes of min heap. Needed for min heapify
void swapMinHeapNode(struct MinHeapNode** a, struct MinHeapNode** b)
{
    struct MinHeapNode* t = *a;
    *a = *b;
    *b = t;
}

// A standard function to heapify at given idx
// This function also updates position of nodes when they are swapped.
// Position is needed for decreaseKey()
void minHeapify(struct MinHeap* minHeap, int idx)
{
    int smallest, left, right;
    smallest = idx;
    left = 2 * idx + 1;
    right = 2 * idx + 2;

    if (left < minHeap->size &&
        minHeap->array[left]->dist < minHeap->array[smallest]->dist )
      smallest = left;

    if (right < minHeap->size &&
        minHeap->array[right]->dist < minHeap->array[smallest]->dist )
      smallest = right;

    if (smallest != idx)
    {
        // The nodes to be swapped in min heap
        MinHeapNode *smallestNode = minHeap->array[smallest];
        MinHeapNode *idxNode = minHeap->array[idx];

        // Swap positions
        minHeap->pos[smallestNode->v] = idx;
        minHeap->pos[idxNode->v] = smallest;

        // Swap nodes
        swapMinHeapNode(&minHeap->array[smallest], &minHeap->array[idx]);

        minHeapify(minHeap, smallest);
    }
}

// A utility function to check if the given minHeap is ampty or not
int isEmpty(struct MinHeap* minHeap)
{
    return minHeap->size == 0;
}

// Standard function to extract minimum node from heap
struct MinHeapNode* extractMin(struct MinHeap* minHeap)
{
    if (isEmpty(minHeap))
        return NULL;

    // Store the root node
    struct MinHeapNode* root = minHeap->array[0];

    // Replace root node with last node
    struct MinHeapNode* lastNode = minHeap->array[minHeap->size - 1];
    minHeap->array[0] = lastNode;

    // Update position of last node
    minHeap->pos[root->v] = minHeap->size-1;
    minHeap->pos[lastNode->v] = 0;

    // Reduce heap size and heapify root
    --minHeap->size;
    minHeapify(minHeap, 0);

    return root;
}

// Function to decreasy dist value of a given vertex v. This function
// uses pos[] of min heap to get the current index of node in min heap
void decreaseKey(struct MinHeap* minHeap, int v, double dist)
{
    // Get the index of v in  heap array
    int i = minHeap->pos[v];

    // Get the node and update its dist value
    minHeap->array[i]->dist = dist;

    // Travel up while the complete tree is not hepified.
    // This is a O(Logn) loop
    while (i && minHeap->array[i]->dist < minHeap->array[(i - 1) / 2]->dist)
    {
        // Swap this node with its parent
        minHeap->pos[minHeap->array[i]->v] = (i-1)/2;
        minHeap->pos[minHeap->array[(i-1)/2]->v] = i;
        swapMinHeapNode(&minHeap->array[i],  &minHeap->array[(i - 1) / 2]);

        // move to parent index
        i = (i - 1) / 2;
    }
}

// A utility function to check if a given vertex
// 'v' is in min heap or not
bool isInMinHeap(struct MinHeap *minHeap, int v)
{
   if (minHeap->pos[v] < minHeap->size)
     return true;
   return false;
}

// A utility function used to print the solution
void printArr(double dist[], int n)
{
    printf("Vertex   Distance from Source\n");
    for (int i = 0; i < n; ++i)
        printf("%d \t\t %f\n", i, dist[i]);
}

// The main function that calulates distances of shortest paths from src to all
// vertices. It is a O(ELogV) function
void dijkstra(struct Graph* graph, int src, int vehicle)
{
    int V = graph->V;// Get the number of vertices in graph
    double dist[V];      // dist values used to pick minimum weight edge in cut
    int trobat=0;
    int numnodes=0;
    // minHeap represents set E
    struct MinHeap* minHeap = createMinHeap(V);

    // Initialize min heap with all vertices. dist value of all vertices
    for (int v = 0; v < V; ++v)
    {
        dist[v]= INT_MAX;
        minHeap->array[v] = newMinHeapNode(v, dist[v]);
        minHeap->pos[v] = v;
    }

    // Make dist value of src vertex as 0 so that it is extracted first
    minHeap->array[src] = newMinHeapNode(src, dist[src]);
    minHeap->pos[src]   = src;
    dist[src]= 0;
    decreaseKey(minHeap, src, dist[src]);

    pred[src].cost[vehicle]=0.0;

    // Initially size of min heap is equal to V
    minHeap->size = V;

    // In the followin loop, min heap contains all nodes
    // whose shortest distance is not yet finalized.
    if(vehicle==0){

        while (!isEmpty(minHeap))
        {
            // Extract the vertex with minimum distance value
            struct MinHeapNode* minHeapNode = extractMin(minHeap);
            int u = minHeapNode->v; // Store the extracted vertex number

            // Traverse through all adjacent vertices of u (the extracted
            // vertex) and update their distance values
            struct AdjListNode* pCrawl = graph->array[u].head;
            while (pCrawl != NULL)
            {
                int v = pCrawl->dest;
                // If shortest distance to v is not finalized yet, and distance to v
                // through u is less than its previously calculated distance
                if (isInMinHeap(minHeap, v) && dist[u] != INT_MAX &&
                                              pCrawl->walkingCost + dist[u] < dist[v])
                {
                    dist[v] = dist[u] + pCrawl->walkingCost;
                    pred[v].pred[0] = u;
                    pred[v].cost[0]=dist[u] +pCrawl->walkingCost;
                    pred[v].data[0]=pCrawl;
                    // update distance value in min heap also
                    decreaseKey(minHeap, v, dist[v]);
                }
                //printf("%f dist\n",dist[v]);
                pCrawl = pCrawl->next;

            }
            if(pred[u].final)
                ++trobat;

        }
    }
    else if(vehicle==1){

        while (!isEmpty(minHeap))
        {
            // Extract the vertex with minimum distance value
            struct MinHeapNode* minHeapNode = extractMin(minHeap);
            int u = minHeapNode->v; // Store the extracted vertex number

            // Traverse through all adjacent vertices of u (the extracted
            // vertex) and update their distance values
            struct AdjListNode* pCrawl = graph->array[u].head;
            while (pCrawl != NULL)
            {
                int v = pCrawl->dest;
                // If shortest distance to v is not finalized yet, and distance to v
                // through u is less than its previously calculated distance

                if (isInMinHeap(minHeap, v) && dist[u] != INT_MAX &&
                                              pCrawl->CarCost + dist[u] < dist[v])
                {
                    dist[v] = dist[u] + pCrawl->CarCost;
                    pred[v].pred[1] = u;
                    pred[v].cost[1] = dist[u] +pCrawl->CarCost;
                    pred[v].data[1] = pCrawl;

                    // update distance value in min heap also
                    decreaseKey(minHeap, v, dist[v]);
                }
                pCrawl = pCrawl->next;
            }
            if(pred[u].final)
                ++trobat;
        }
    }
    else if(vehicle==2){
        while (!isEmpty(minHeap))
        {
            // Extract the vertex with minimum distance value
            struct MinHeapNode* minHeapNode = extractMin(minHeap);
            int u = minHeapNode->v; // Store the extracted vertex number

            // Traverse through all adjacent vertices of u (the extracted
            // vertex) and update their distance values
            struct AdjListNode* pCrawl = graph->array[u].head;
            while (pCrawl != NULL)
            {
                int v = pCrawl->dest;
                // If shortest distance to v is not finalized yet, and distance to v
                // through u is less than its previously calculated distance
                if (isInMinHeap(minHeap, v) && dist[u] != INT_MAX &&
                                              pCrawl->BRPCost + dist[u] < dist[v])
                {
                    dist[v] = dist[u] + pCrawl->BRPCost;
                    pred[v].pred[2] = u;
                    pred[v].cost[2] = dist[u] +pCrawl->BRPCost;
                    pred[v].data[2]=pCrawl;

                    // update distance value in min heap also
                    decreaseKey(minHeap, v, dist[v]);
                }
                //printf("%f dist\n",dist[v]);
                pCrawl = pCrawl->next;
            }
            if(pred[u].final)
                ++trobat;
        }
    }
    else if(vehicle==3){
        while (!isEmpty(minHeap))
        {
            // Extract the vertex with minimum distance value
            struct MinHeapNode* minHeapNode = extractMin(minHeap);
            int u = minHeapNode->v; // Store the extracted vertex number

            // Traverse through all adjacent vertices of u (the extracted
            // vertex) and update their distance values
            struct AdjListNode* pCrawl = graph->array[u].head;
            while (pCrawl != NULL)
            {
                int v = pCrawl->dest;
                // If shortest distance to v is not finalized yet, and distance to v
                // through u is less than its previously calculated distance
                if ( isInMinHeap(minHeap, v) && dist[u] != INT_MAX &&
                                              pCrawl->AllTerrainCost + dist[u] < dist[v])
                {
                    dist[v] = dist[u] + pCrawl->AllTerrainCost;
                    pred[v].pred[3] = u;
                    pred[v].cost[3]=dist[u] +pCrawl->AllTerrainCost;
                    pred[v].data[3]=pCrawl;
                    // update distance value in min heap also
                    decreaseKey(minHeap, v, dist[v]);
                }
                //printf("%f dist\n",dist[v]);
                pCrawl = pCrawl->next;
            }
        }
    }

    // print the calculated shortest distances
    //printArr(dist, V);
}

/*
extern "C" void memorize(char file[]);
extern "C" int *routing(int end, int start);*/
struct Graph* globalGraph;
extern "C" void inizializeGraph(int V);
extern "C" int findKey(long long nodeId);
extern "C" long long *findPredecesor(int key,int vehicle);
extern "C" double *findPredecesorValues(int key,int vehicle);
extern "C" void solve(long long start, int vehicle);
extern "C" void inicializeEdge(int nodeKey1,int nodeKey2, double walkingCost,double CarCost,double BRPCost,double AllTerrainCost,double rampPos, double rampNeg, double dist);
extern "C" int addNode(long long nodeKey);
extern "C" void addfinal(int nodeKey);
extern "C" void addVehicle(int type, int node);
extern "C" void delateVehicles();
extern "C" double getMaxValue();
extern "C" double *costValuesOfNode(int src, int dest);

void addfinal(int nodeKey){
    ++numFianls;
    pred[nodeKey].final=true;
}

double getMaxValue(){
    return INT_MAX;
}
/*
for (int i = 0; i < V; ++i){
        graph->array[i].head = NULL;
        nodes[i]=0;
        final[i]=false;

*/
void delateVehicles(){
    for (int v = 0; v < MAX; ++v)
    {
        vehicles[v][0]=vehicles[v][1]=vehicles[v][2]=0;
    }
}

void addVehicle(int type, int node) {
    int nodekey = -1;
    for(int i =0; i<numNode;++i){
        if(nodes[i]==node){
            nodekey=i;
        }
    }
    if(nodekey>-1)
        ++vehicles[nodekey][type-1];
}

void inizializeGraph(int V){

    for(int i =0; i<numNode;++i){
        pred[i].final=false;
    }
    globalGraph = createGraph(V);
}


double *costValuesOfNode( int src, int dest){
    double * returnValue =(double *) malloc(sizeof(double) * 4);
    ////////////
    struct AdjListNode* pCrawl = globalGraph->array[src].head;
    while (pCrawl != NULL && pCrawl->dest!=dest)
    {
        //printf("%f dist\n",dist[v]);
        pCrawl = pCrawl->next;
    }
    if(pCrawl != NULL) {
        returnValue[0]=pCrawl->walkingCost;
        returnValue[1]=pCrawl->CarCost;
        returnValue[2]=pCrawl->BRPCost;
        returnValue[3]=pCrawl->AllTerrainCost;
    }
    ////////////
    return returnValue;
}

int addNode(long long nodeKey){
    nodes[numNode]=nodeKey;
    ++numNode;
    return numNode-1;
}

void inicializeEdge(int node1,int node2, double walkingCost,double CarCost,double BRPCost,double AllTerrainCost, double rampPos, double rampNeg, double dist){

    addEdge(globalGraph, node1, node2, walkingCost, CarCost, BRPCost, AllTerrainCost, rampPos, rampNeg, dist);
}

void solve(long long start, int vehicle){
    for(int i =0; i<numNode;++i){
        if(nodes[i]==start){
            start=i;
        }
    }
    dijkstra(globalGraph, start,vehicle);
}

long long *findPredecesor(int key,int vehicle){
    long long * returnValue =(long long *) malloc(sizeof(long long) * 3);
    returnValue[0]=pred[key].pred[vehicle];
    returnValue[1]=nodes[pred[key].pred[vehicle]];
    returnValue[2]=vehicle;
    return returnValue;
}



double *findPredecesorValues(int key,int vehicle){
    double * returnValue =(double *) malloc(sizeof(double) * 8);
    struct AdjListNode* pCrawl =  pred[key].data[vehicle];
    returnValue[3]=pred[key].cost[vehicle];
    returnValue[0]=pCrawl->rampPos;
    returnValue[1]=pCrawl->rampNeg;
    returnValue[2]=pCrawl->dist;
    returnValue[4]=pCrawl->walkingCost;
    returnValue[5]=pCrawl->CarCost;
    returnValue[6]=pCrawl->BRPCost;
    returnValue[7]=pCrawl->AllTerrainCost;
    ////////////
    return returnValue;
/*
    double rampPos[4];
    double rampNeg[4];
    double dist[4];
    double * returnValue =(double *) malloc(sizeof(double) * 4);
    returnValue[0]=pred[key].rampPos[vehicle];
    returnValue[1]=pred[key].rampNeg[vehicle];
    returnValue[2]=pred[key].dist[vehicle];
    returnValue[3]=pred[key].cost[vehicle];
    return returnValue;*/
}

int findKey(long long nodeId){
    int value=-1;
    for(int i =0; i<numNode;++i){
        if(nodes[i]==nodeId){
            value=i;
        }
    }
    return value;
}


/*
// Driver program to test above functions
int main()
{
    // create the graph given in above fugure
    int V = MAX;
    struct Graph* graph = createGraph(V);

    FILE * fp;
    char * line = NULL;
    char * idtoAll = NULL;
    char * idtoParse = NULL;
    char * idtoRest = NULL;
    char * id=NULL;
    int node1=0;
    int node2=0;
	int start=-172242;
	int ends[6]={-47998,-83910,-53840,-136928,-74118,-103972};
    //void addEdge(struct Graph* graph, int src, int dest, int weight)
    int numNode=0;
    size_t len = 0;
    ssize_t read;
    printf("FILE\n");
    fp = fopen("./connexioGRAPH2.osm", "r");
    if (fp == NULL)
        exit(EXIT_FAILURE);
    while ((read = getline(&line, &len, fp)) != -1) {
        if(strstr(line,"<node")!=NULL){

            idtoAll=strstr(line,"id='");
            idtoParse=strstr(idtoAll,"-");
            idtoRest=strstr(idtoParse,"' ");
            idtoRest[0]='\0';
            nodes[numNode]=atoi(idtoParse);
            ++numNode;
  //<node id='-122474' action='modify' lat='41.55136910003' lon='1.78672119968' >
        }
        if(strstr(line,"<way")!=NULL){
            while(strstr(line,"<nd")==NULL){
                read = getline(&line, &len, fp);
            }
            idtoAll=strstr(line,"ref='");
            idtoParse=strstr(idtoAll,"-");
            idtoRest=strstr(idtoParse,"' ");
            idtoRest[0]='\0';
            node1=atoi(idtoParse);
            read = getline(&line, &len, fp);
            while(strstr(line,"<nd")==NULL){
                read = getline(&line, &len, fp);
            }
            idtoAll=strstr(line,"ref='");
            idtoParse=strstr(idtoAll,"-");
            idtoRest=strstr(idtoParse,"' ");
            idtoRest[0]='\0';
            node2=atoi(idtoParse);
            for(int i =0; i<numNode;++i){
                if(nodes[i]==node1){
                    node1=i;
                }
                if(nodes[i]==node2){
                    node2=i;
                }
            }
            read = getline(&line, &len, fp);
            while(strstr(line,"k='Distance_From_")==NULL){
                read = getline(&line, &len, fp);
            }
            idtoAll=strstr(line,"v='");
            memmove(idtoAll, idtoAll+3, strlen(idtoAll));
            idtoRest=strstr(idtoAll,"' ");
            idtoRest[0]='\0';
            //if(atof(idtoAll)!=0.0)
            //G[node1][node2] = G[node2][node1] = atof(idtoAll);
            addEdge(graph, node1, node2, atof(idtoAll));
        }
    }

    printf("file readed\n");
    for(int i =0; i<numNode;++i){
        if(nodes[i]==start){
            final[i]=false;
            start=i;
        }
        else if(nodes[i]==ends[0]){
            final[i]=true;
            ends[0]=i;
        }
        else if(nodes[i]==ends[1]){
            final[i]=true;
            ends[1]=i;
        }
        else if(nodes[i]==ends[2]){
            final[i]=true;
            ends[2]=i;
        }
        else if(nodes[i]==ends[3]){
            final[i]=true;
            ends[3]=i;
        }
        else if(nodes[i]==ends[4]){
            final[i]=true;
            ends[4]=i;
        }
        else if(nodes[i]==ends[5]){
            final[i]=true;
            ends[5]=i;
        }
        else{
            final[i]=false;
        }
    }
    printf("dijkstra\n");
    int numFinals = (sizeof(ends)/sizeof(*ends));
    dijkstra(graph, start,numFinals);
    printf("search\n");

    for (int i=0; i<numFinals; ++i){
        int end=ends[i];
        int k=0;
        int j=end;
        printf("%d",nodes[end]);
        do
        {
            ++k;
            j=pred[j].pred;
            printf("<-%d",nodes[j]);
            //route[k]=nodes[j];
            //printf("G %f",G[ends[i]][start]);
        }while(j!=start);
        printf("<--%d\nnum Nodes %d;\n\n",nodes[start],k);


    }
    printf("end\n");

    return 0;
}*/