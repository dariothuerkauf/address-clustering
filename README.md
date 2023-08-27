# address-clustering
Master Thesis

Title: Developing Address Clustering Heuristics for Account-Based Blockchain Networks: An Analysis based on a Specific Address Set

Author: Dario Thürkauf

Supervisor: Prof. Dr. Fabian Schär

## Structure
- `python`: Contains all the source code used for data collection, analysis, and visualization.
- `figures`: Contains all the generated figures and plots generated.
- `data`: Contains the small data sets used for the analysis.

## Abstract
Given the negligible cost of creating blockchain addresses, the notion that one address equates to one user is flawed. Therefore, Blockchain Address Clustering emerges as a key tool for estimating the actual number of users. This paper examines heuristics to cluster addresses using Ethereum and Polygon PoS data, analyzing over 470,000 addresses collected from Decentraland over the course of nine months. We assess various existing heuristics, adapt them to our specific research context, and also introduce a new heuristic. Our findings suggest that graph representation learning, particularly the application of an existing node embedding algorithm to an asset transfer network graph, is the most effective approach for clustering a predefined address set. However, the method does not come without its drawbacks, which is why we propose possible extensions for improving clustering performance.
