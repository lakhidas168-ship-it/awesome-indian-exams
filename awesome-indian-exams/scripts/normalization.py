import math
import os

def calculate_ssc_normalized_score(m_ij, m_ti, m_iq, m_gm, m_ga, m_qa):
    """
    SSC Normalization Formula:
    M_ij = (M_gm - M_ga) / (M_ti - M_iq) * (M_ij - M_iq) + M_qa
    
    Reference: https://ssc.gov.in/api/assets/uploads/Notice_for_Normalization_of_Marks.pdf
    """
    if (m_ti - m_iq) == 0:
        return float(m_ij)
    return (m_gm - m_ga) / (m_ti - m_iq) * (m_ij - m_iq) + m_qa

def main():
    print("SSC Normalization Calculator")
    print("Reference: https://ssc.gov.in/api/assets/uploads/Notice_for_Normalization_of_Marks.pdf")
    try:
        m_ij = float(input("Enter candidate's raw marks (M_ij): "))
        m_ti = float(input("Enter mean marks of top 0.1% in shift (M_ti): "))
        m_iq = float(input("Enter mean marks of shift (M_iq): "))
        m_gm = float(input("Enter global mean marks (M_gm): "))
        m_ga = float(input("Enter global mean marks of top 0.1% (M_ga): "))
        m_qa = float(input("Enter global mean marks (M_qa): "))
        
        result = calculate_ssc_normalized_score(m_ij, m_ti, m_iq, m_gm, m_ga, m_qa)
        print(f"Normalized Marks: {result:.2f}")
    except ValueError:
        print("Invalid input. Please enter numeric values.")

if __name__ == "__main__":
    main()
