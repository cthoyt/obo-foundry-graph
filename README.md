# obo-foundry-graph

A demonstration of building a unified knowledge graph of OBO Foundry ontologies
building on [ROBOT](https://robot.obolibrary.org/) for parsing ontologies,
[`bioontologies`](https://github.com/biopragmatics/bioontologies) for wrapping
ROBOT in Python and providing an object model of
[OBO Graph JSON](https://github.com/geneontology/obographs), and the
[Bioregistry](https://github.com/biopragmatics/bioregistry) for standardization.

## Data

### [`graph.tsv.gz`](graph.tsv.gz)

The graph is a gzipped tab-separated values file that contains the following
columns:

1. `subjet` - the subject entity as a CURIE when possible to normalize
2. `prediate` - the predicate entity as a CURIE when possible to normalize
3. `object` - the object entity as a CURIE when possible to normalize
4. `sources` - a pipe-delimited list of ontologies in which the triple was found

## Build

The graph can be re-built with the following code:

```shell
$ git clone https://github.com/cthoyt/obo-foundry-graph.git
$ cd obo-foundry-graph
$ pip install tox
$ tox 
```
