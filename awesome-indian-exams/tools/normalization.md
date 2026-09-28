# Normalization Calculator

This tool provides a normalization calculator based on the official SSC formula.

## Formula
The formula used is:
$M_{ij} = \frac{M_{gm} - M_{ga}}{M_{ti} - M_{iq}} \times (M_{ij} - M_{iq}) + M_{qa}$

Where:
- $M_{ij}$: Normalized marks of j-th candidate in i-th shift
- $M_{ti}$: Mean marks of top 0.1% candidates in i-th shift
- $M_{iq}$: Mean marks of i-th shift
- $M_{gm}$: Global mean marks of all shifts
- $M_{ga}$: Global mean marks of top 0.1% candidates of all shifts
- $M_{qa}$: Global mean marks of all shifts

## Official Source
[SSC Notice for Normalization of Marks](https://ssc.gov.in/api/assets/uploads/Notice_for_Normalization_of_Marks.pdf)

## Usage
Run the calculator using:
`python3 scripts/normalization.py`
