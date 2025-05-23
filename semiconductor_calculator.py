import numpy as np
from scipy.optimize import brentq
import matplotlib.pyplot as plt

# === Universal Physical Constants ===
k_B_J_per_K = 1.380649e-23  # Boltzmann constant in J/K
k_B_eV_per_K = 8.617333262145e-5  # Boltzmann constant in eV/K
q_C = 1.602176634e-19  # Elementary charge in Coulombs (C)
m_0_kg = 9.1093837015e-31  # Free electron rest mass in kg
h_Js = 6.62607015e-34  # Planck constant in J·s
hbar_Js = 1.054571817e-34  # Reduced Planck constant (h/2π) in J·s
epsilon_0_F_per_m = 8.8541878128e-12  # Vacuum permittivity in F/m

# === GaAs Material Parameters ===
# Note: These are example parameters for Gallium Arsenide (GaAs)
m_e_star_GaAs_kg = 0.063 * m_0_kg  # Effective electron mass for GaAs in kg
m_dp_star_GaAs_kg = 0.53 * m_0_kg  # Density of states effective mass for holes in GaAs in kg
epsilon_s_GaAs_relative = 12.9  # Static relative dielectric constant for GaAs (dimensionless)
Eg0_GaAs_eV = 1.519  # Energy gap at 0K for GaAs (Varshni parameter) in eV
alpha_Eg_GaAs_eV_per_K = 5.405e-4  # Varshni alpha coefficient for GaAs band gap in eV/K
beta_Eg_GaAs_K = 204.0  # Varshni beta coefficient (Debye temperature) for GaAs band gap in K
Nd_GaAs_per_m3 = 1.5e16 * (100.0**3)  # Tellurium (Te) donor concentration in m^-3 (converted from 1.5e16 cm^-3)
Ed_GaAs_eV = 0.03  # Te donor ionization energy in eV, relative to the conduction band edge (E_c)
g_D_GaAs = 2.0  # Donor degeneracy factor for Te in GaAs (dimensionless)
mu_L0_GaAs_m2_per_Vs = 8500.0 * (0.01**2)  # Reference lattice mobility for electrons at 300K in m^2/(V·s) (converted from 8500 cm^2/(V·s))
s_L_GaAs = 2.1  # Temperature exponent for electron lattice mobility (dimensionless)
kappa_L_300_GaAs_W_per_mK = 0.50 * 100.0  # Lattice thermal conductivity at 300K in W/(m·K) (converted from 0.50 W/(cm·K))
s_kappa_GaAs = 1.3  # Temperature exponent for lattice thermal conductivity (dimensionless)
r_H_GaAs_300K = 1.2  # Hall scattering factor at 300K for GaAs (dimensionless)
Ac_seebeck_GaAs_dimensionless = 2.5  # Transport constant for Seebeck coefficient (dimensionless), assumes r_s = 0 where Ac = r_s + 2.5

# === Calculation Functions ===

def calculate_Eg_eV(T_K, Eg0_eV, alpha_eV_per_K, beta_K):
    """
    Calculates Energy Gap (E_g) in eV using Varshni's empirical equation.

    Parameters:
        T_K (float): Temperature in Kelvin (K).
        Eg0_eV (float): Energy gap at 0K in electronVolts (eV).
        alpha_eV_per_K (float): Varshni alpha coefficient in eV/K.
        beta_K (float): Varshni beta coefficient (Debye temperature) in K.

    Returns:
        float: Energy gap (E_g) at temperature T_K in eV.
    """
    return Eg0_eV - (alpha_eV_per_K * T_K**2) / (T_K + beta_K)

def calculate_Nc_Nv_per_m3(T_K, m_eff_kg, k_B_J_per_K_local=k_B_J_per_K, h_Js_local=h_Js):
    """
    Calculates Nc or Nv (effective density of states in conduction/valence band) in m^-3.

    Parameters:
        T_K (float): Temperature in Kelvin (K).
        m_eff_kg (float): Effective mass of electron or hole in kg.
        k_B_J_per_K_local (float, optional): Boltzmann constant in J/K. Defaults to global k_B_J_per_K.
        h_Js_local (float, optional): Planck constant in J·s. Defaults to global h_Js.

    Returns:
        float: Effective density of states (Nc or Nv) in m^-3.
    """
    return 2 * ( (2 * np.pi * m_eff_kg * k_B_J_per_K_local * T_K) / (h_Js_local**2) )**(3/2)

def calculate_lattice_mobility_electron_m2_per_Vs(T_K, mu_L0_m2_per_Vs, s_L, T0_K=300.0):
    """
    Calculates electron lattice mobility (μ_L) in m^2/(V·s) using a power-law temperature dependence.

    Parameters:
        T_K (float): Temperature in Kelvin (K).
        mu_L0_m2_per_Vs (float): Reference lattice mobility at T0_K in m^2/(V·s).
        s_L (float): Temperature exponent for lattice mobility (dimensionless).
        T0_K (float, optional): Reference temperature in Kelvin (K). Defaults to 300.0 K.

    Returns:
        float: Electron lattice mobility (μ_L) at temperature T_K in m^2/(V·s).
    """
    return mu_L0_m2_per_Vs * (T_K / T0_K)**(-s_L)

def calculate_lattice_thermal_conductivity_W_per_mK(T_K, kappa_L0_W_per_mK, s_kappa, T0_K=300.0):
    """
    Calculates lattice thermal conductivity (κ_L) in W/(m·K) using a power-law temperature dependence.

    Parameters:
        T_K (float): Temperature in Kelvin (K).
        kappa_L0_W_per_mK (float): Reference lattice thermal conductivity at T0_K in W/(m·K).
        s_kappa (float): Temperature exponent for lattice thermal conductivity (dimensionless).
        T0_K (float, optional): Reference temperature in Kelvin (K). Defaults to 300.0 K.

    Returns:
        float: Lattice thermal conductivity (κ_L) at temperature T_K in W/(m·K).
    """
    return kappa_L0_W_per_mK * (T_K / T0_K)**(-s_kappa)

def calculate_total_mobility_electron_m2_per_Vs(mu_L_m2_per_Vs, mu_I_m2_per_Vs):
    """
    Calculates total electron mobility (μ_total) in m^2/(V·s) using Matthiessen's rule.
    Handles cases where one or both mobilities are very small (effectively zero).

    Parameters:
        mu_L_m2_per_Vs (float): Lattice mobility in m^2/(V·s).
        mu_I_m2_per_Vs (float): Ionized impurity mobility in m^2/(V·s).

    Returns:
        float: Total electron mobility (μ_total) in m^2/(V·s).
    """
    if mu_L_m2_per_Vs <= 1e-9 and mu_I_m2_per_Vs <= 1e-9: # If both are effectively zero
        return 1e-9 
    if mu_L_m2_per_Vs <= 1e-9 : # If only lattice mobility is zero
        return mu_I_m2_per_Vs 
    if mu_I_m2_per_Vs <= 1e-9: # If only ionized impurity mobility is zero
        return mu_L_m2_per_Vs 
    return 1 / (1/mu_L_m2_per_Vs + 1/mu_I_m2_per_Vs) # Matthiessen's Rule

def calculate_conductivity_S_per_m(n_per_m3, mu_total_m2_per_Vs):
    """
    Calculates electrical conductivity (σ) in S/m (Siemens per meter).
    Uses the global constant q_C for elementary charge.

    Parameters:
        n_per_m3 (float): Electron concentration in m^-3.
        mu_total_m2_per_Vs (float): Total electron mobility in m^2/(V·s).

    Returns:
        float: Electrical conductivity (σ) in S/m.
    """
    return n_per_m3 * q_C * mu_total_m2_per_Vs

def calculate_ionized_impurity_mobility_electron_m2_per_Vs(
    T_K, n_per_m3, N_ion_per_m3, m_eff_kg, epsilon_s_relative, 
    k_B_J_per_K_local, epsilon_0_F_per_m_local, q_C_local, hbar_Js_local
):
    """
    Calculates electron mobility due to ionized impurity scattering (μ_I) 
    in m^2/(V·s) using the Brooks-Herring formula.

    Parameters:
        T_K (float): Temperature in Kelvin (K).
        n_per_m3 (float): Electron concentration in m^-3 (used for screening length).
        N_ion_per_m3 (float): Total ionized impurity concentration in m^-3.
        m_eff_kg (float): Effective electron mass in kg.
        epsilon_s_relative (float): Relative static dielectric constant (dimensionless).
        k_B_J_per_K_local (float): Boltzmann constant in J/K.
        epsilon_0_F_per_m_local (float): Vacuum permittivity in F/m.
        q_C_local (float): Elementary charge in Coulombs (C).
        hbar_Js_local (float): Reduced Planck constant in J·s.

    Returns:
        float: Ionized impurity mobility (μ_I) in m^2/(V·s). 
               Returns a very large number (1e12) if scattering is negligible (e.g., N_ion_per_m3 is near zero).
               Returns a very small number (1e-9) if inputs are problematic (e.g., n_per_m3 is near zero).
    """
    if n_per_m3 <= 1e-6: # Avoid division by zero for Debye length if n is too small (e.g. < 1 cm^-3)
        return 1e-9 # Indicates very low mobility or problematic input

    # 1. Calculate the Debye screening length (lambda_D_m)
    lambda_D_m_sq_numerator = (epsilon_0_F_per_m_local * epsilon_s_relative * k_B_J_per_K_local * T_K)
    lambda_D_m_sq_denominator = (q_C_local**2 * n_per_m3)
    if lambda_D_m_sq_denominator <= 1e-30: # Denominator too small
         return 1e-9 
    lambda_D_m_sq = lambda_D_m_sq_numerator / lambda_D_m_sq_denominator
    if lambda_D_m_sq < 0: # Unphysical
        return 1e-9
    lambda_D_m = np.sqrt(lambda_D_m_sq)

    # 2. Calculate the screening parameter b_BH_sq for Brooks-Herring
    b_BH_sq_numerator = (8 * m_eff_kg * k_B_J_per_K_local * T_K * lambda_D_m**2)
    b_BH_sq_denominator = hbar_Js_local**2
    if b_BH_sq_denominator <= 1e-70: # hbar^2 too small (should not happen with standard constants)
        return 1e-9
    b_BH_sq = b_BH_sq_numerator / b_BH_sq_denominator

    # 3. Calculate the screening function G_BH for Brooks-Herring
    if (1 + b_BH_sq) <= 1e-9: # Avoid log(0) or division by very small number if (1+b_BH_sq) is near zero (unphysical)
        return 1e-9 
    
    if b_BH_sq < 1e-9 : # If b_BH_sq is very small, use Taylor expansion for G_BH to avoid numerical issues
        G_BH = b_BH_sq**2 / 2 # log(1+x) - x/(1+x) approx x^2/2 for small x
        if G_BH <= 1e-18: # If G_BH is effectively zero after expansion
             return 1e12 # Very high mobility (negligible scattering)
    else:
        G_BH = np.log(1 + b_BH_sq) - (b_BH_sq / (1 + b_BH_sq))

    if G_BH <= 1e-9: # If G_BH is zero or very small, mobility is very high
        return 1e12  

    if N_ion_per_m3 <= 1e-6: # If no significant ionized impurities, mobility is effectively infinite
        return 1e12 

    # 4. Calculate the mobility mu_I using Brooks-Herring formula
    coeff_numerator = (128 * np.sqrt(2 * np.pi) * 
                       (epsilon_0_F_per_m_local * epsilon_s_relative)**2 * 
                       (k_B_J_per_K_local * T_K)**1.5)
    coeff_denominator = (q_C_local**3 * np.sqrt(m_eff_kg) * N_ion_per_m3)

    if coeff_denominator <= 1e-70 or m_eff_kg <=0 : # Denominator too small or unphysical mass
        return 1e-9 
    
    coeff = coeff_numerator / coeff_denominator
    mu_I = coeff / G_BH
    
    return mu_I

def calculate_fermi_level_and_carriers_n_type(
    T_K, Eg0_eV, alpha_Eg_eV_per_K, beta_Eg_K, 
    m_e_eff_kg, m_h_eff_kg, N_d_per_m3, E_d_eV, g_D,
    k_B_eV_per_K_const, k_B_J_per_K_const, h_Js_const
):
    """
    Calculates the Fermi level (E_F), electron concentration (n), and 
    ionized donor concentration (N_D+) for an n-type semiconductor.
    E_F is referenced from the valence band maximum (E_v = 0).

    Parameters:
        T_K (float): Temperature in Kelvin (K).
        Eg0_eV (float): Energy gap at 0K in eV (Varshni parameter).
        alpha_Eg_eV_per_K (float): Varshni alpha coefficient in eV/K.
        beta_Eg_K (float): Varshni beta coefficient in K.
        m_e_eff_kg (float): Electron effective mass in kg.
        m_h_eff_kg (float): Hole effective mass in kg.
        N_d_per_m3 (float): Total donor concentration in m^-3.
        E_d_eV (float): Donor ionization energy in eV (distance from E_c).
        g_D (float): Donor degeneracy factor (dimensionless).
        k_B_eV_per_K_const (float): Boltzmann constant in eV/K.
        k_B_J_per_K_const (float): Boltzmann constant in J/K.
        h_Js_const (float): Planck constant in J·s.

    Returns:
        tuple: (E_F_eV, n_per_m3, N_D_plus_per_m3)
               E_F_eV (float): Fermi level in eV, referenced from E_v = 0.
               n_per_m3 (float): Electron concentration in m^-3.
               N_D_plus_per_m3 (float): Ionized donor concentration in m^-3.
    """
    # 1. Calculate temperature-dependent Energy Gap (E_g)
    Eg_eV_val = calculate_Eg_eV(T_K, Eg0_eV, alpha_Eg_eV_per_K, beta_Eg_K)

    # 2. Calculate Effective Density of States for Conduction Band (Nc)
    Nc_per_m3_val = calculate_Nc_Nv_per_m3(T_K, m_e_eff_kg, k_B_J_per_K_const, h_Js_const)

    # 3. Calculate Effective Density of States for Valence Band (Nv)
    Nv_per_m3_val = calculate_Nc_Nv_per_m3(T_K, m_h_eff_kg, k_B_J_per_K_const, h_Js_const)

    # Donor energy level (E_D_level_eV) is referenced from E_v = 0.
    # E_d_eV is the energy required to ionize a donor, measured from E_c.
    E_D_level_eV = Eg_eV_val - E_d_eV 

    # 4. Define the charge neutrality equation function for the root solver
    # The function aims to find E_F_eV_trial where (n - p - N_D+) = 0.
    def charge_neutrality_func(E_F_eV_trial):
        # Electron concentration (n_trial) using Boltzmann approximation
        # E_c = Eg_eV_val (since E_v = 0)
        exp_n_arg = -(Eg_eV_val - E_F_eV_trial) / (k_B_eV_per_K_const * T_K)
        if exp_n_arg > 700: n_trial = np.inf # Avoid np.exp overflow
        elif exp_n_arg < -700: n_trial = 0.0 # Avoid np.exp underflow
        else: n_trial = Nc_per_m3_val * np.exp(exp_n_arg)
        
        # Hole concentration (p_trial) using Boltzmann approximation
        # E_v = 0
        exp_p_arg = -E_F_eV_trial / (k_B_eV_per_K_const * T_K)
        if exp_p_arg > 700: p_trial = np.inf
        elif exp_p_arg < -700: p_trial = 0.0
        else: p_trial = Nv_per_m3_val * np.exp(exp_p_arg)

        # Ionized donor concentration (N_D_plus_trial)
        exp_Nd_arg = (E_F_eV_trial - E_D_level_eV) / (k_B_eV_per_K_const * T_K)
        if exp_Nd_arg > 700: # exp term is huge, denominator is huge, N_D_plus_trial approaches 0
            N_D_plus_trial = 0.0
        elif exp_Nd_arg < -700: # exp term is tiny, denominator is approx 1, N_D_plus_trial approaches N_d_per_m3
             N_D_plus_trial = N_d_per_m3
        else:
            N_D_plus_trial = N_d_per_m3 / (1 + g_D * np.exp(exp_Nd_arg))
            
        return n_trial - p_trial - N_D_plus_trial # Charge neutrality condition

    # 5. Solve for E_F_eV using scipy.optimize.brentq numerical root finder
    # Initial search bounds for Fermi level (E_F), referenced from E_v = 0.
    search_min_eV = -0.5  # Robust lower bound, typically well below E_v
    search_max_eV = Eg_eV_val + 0.5 # Robust upper bound, typically well above E_c

    try:
        f_min = charge_neutrality_func(search_min_eV)
        f_max = charge_neutrality_func(search_max_eV)
        # Brentq requires the function to have different signs at the bounds.
        if np.sign(f_min) == np.sign(f_max):
            # Fallback: try alternative search range if initial bounds have same sign.
            # This might happen in extreme doping/temperature cases.
            search_min_eV_alt = E_D_level_eV - 20 * k_B_eV_per_K_const * T_K # Centered around donor level
            search_max_eV_alt = E_D_level_eV + 20 * k_B_eV_per_K_const * T_K
            f_min_alt = charge_neutrality_func(search_min_eV_alt)
            f_max_alt = charge_neutrality_func(search_max_eV_alt)
            if np.sign(f_min_alt) != np.sign(f_max_alt):
                search_min_eV = search_min_eV_alt
                search_max_eV = search_max_eV_alt
            else: 
                # Further fallback if alternative also fails, try tighter bounds around E_D
                search_min_eV = E_D_level_eV - 2 * k_B_eV_per_K_const * T_K
                search_max_eV = E_D_level_eV + 2 * k_B_eV_per_K_const * T_K
        # Find the root (Fermi Level)
        E_F_eV = brentq(charge_neutrality_func, search_min_eV, search_max_eV, xtol=1e-6, rtol=1e-6, maxiter=100)
    except ValueError:
        # If brentq fails (e.g., no sign change even with fallbacks, or other convergence issue),
        # use a simple approximation for E_F. This is a fallback and might not be accurate.
        E_F_eV = E_D_level_eV 

    # 6. Recalculate n_per_m3 and N_D_plus_per_m3 with the found E_F_eV for consistency
    exp_n_final_arg = -(Eg_eV_val - E_F_eV) / (k_B_eV_per_K_const * T_K)
    if exp_n_final_arg > 700: n_final_per_m3 = np.inf
    elif exp_n_final_arg < -700: n_final_per_m3 = 0.0
    else: n_final_per_m3 = Nc_per_m3_val * np.exp(exp_n_final_arg)

    exp_Nd_final_arg = (E_F_eV - E_D_level_eV) / (k_B_eV_per_K_const * T_K)
    if exp_Nd_final_arg > 700: N_D_plus_final_per_m3 = 0.0
    elif exp_Nd_final_arg < -700: N_D_plus_final_per_m3 = N_d_per_m3
    else: N_D_plus_final_per_m3 = N_d_per_m3 / (1 + g_D * np.exp(exp_Nd_final_arg))

    # 7. Return the calculated Fermi level and carrier concentrations
    return E_F_eV, n_final_per_m3, N_D_plus_final_per_m3

# === Main Execution Block ===
if __name__ == "__main__":
    
    # --- Section 1: Temperature Array Setup and Loop for Generating Data Arrays ---
    T_array_K = np.linspace(50, 600, 100) # Define temperature range in Kelvin

    # Initialize lists to store results from the temperature loop
    temp_results_K = []
    ln_n_results = []           # For ln(electron concentration)
    inv_T_results_per_K = []    # For inverse temperature (1/T)
    Ef_results_eV = []          # For Fermi level
    mu_total_results_m2_per_Vs = [] # For total mobility
    mu_L_results_m2_per_Vs = []     # For lattice mobility
    mu_I_results_m2_per_Vs = []     # For ionized impurity mobility
    ln_sigma_results = []       # For ln(electrical conductivity)
    n_results_per_m3 = []       # For electron concentration
    sigma_results_S_per_m = []  # For electrical conductivity

    # Loop through each temperature in the array
    for T_K_loop in T_array_K:
        # Calculate Fermi level (E_F), electron concentration (n), and ionized donor concentration (N_D+)
        E_F_eV_val, n_per_m3_val, N_D_plus_per_m3_val = calculate_fermi_level_and_carriers_n_type(
            T_K_loop, Eg0_GaAs_eV, alpha_Eg_GaAs_eV_per_K, beta_Eg_GaAs_K,
            m_e_star_GaAs_kg, m_dp_star_GaAs_kg, Nd_GaAs_per_m3, Ed_GaAs_eV, g_D_GaAs,
            k_B_eV_per_K, k_B_J_per_K, h_Js # Pass relevant constants
        )
        
        # Calculate lattice mobility (μ_L)
        mu_L_m2_per_Vs_val = calculate_lattice_mobility_electron_m2_per_Vs(
            T_K_loop, mu_L0_GaAs_m2_per_Vs, s_L_GaAs
        )
        
        # Calculate ionized impurity mobility (μ_I)
        # N_ion_per_m3 (total ionized impurity concentration) is assumed to be N_D_plus_per_m3_val for n-type
        mu_I_m2_per_Vs_val = calculate_ionized_impurity_mobility_electron_m2_per_Vs(
            T_K_loop, n_per_m3_val, N_D_plus_per_m3_val, m_e_star_GaAs_kg, epsilon_s_GaAs_relative,
            k_B_J_per_K, epsilon_0_F_per_m, q_C, hbar_Js # Pass relevant constants
        )
        
        # Calculate total electron mobility (μ_total) using Matthiessen's rule
        mu_total_m2_per_Vs_val = calculate_total_mobility_electron_m2_per_Vs(
            mu_L_m2_per_Vs_val, mu_I_m2_per_Vs_val
        )
        
        # Calculate electrical conductivity (σ)
        sigma_S_per_m_val = calculate_conductivity_S_per_m(
            n_per_m3_val, mu_total_m2_per_Vs_val # q_C is used globally in this function
        )

        # Append results to their respective lists
        temp_results_K.append(T_K_loop)
        inv_T_results_per_K.append(1.0 / T_K_loop)
        Ef_results_eV.append(E_F_eV_val)
        mu_L_results_m2_per_Vs.append(mu_L_m2_per_Vs_val)
        mu_I_results_m2_per_Vs.append(mu_I_m2_per_Vs_val)
        mu_total_results_m2_per_Vs.append(mu_total_m2_per_Vs_val)
        n_results_per_m3.append(n_per_m3_val)
        sigma_results_S_per_m.append(sigma_S_per_m_val)

        # Calculate natural log of n, handling potential non-positive or invalid values
        if n_per_m3_val > 0 and not np.isinf(n_per_m3_val) and not np.isnan(n_per_m3_val):
            ln_n_results.append(np.log(n_per_m3_val))
        else:
            ln_n_results.append(np.nan) # Use NaN for invalid log inputs

        # Calculate natural log of sigma, handling potential non-positive or invalid values
        if sigma_S_per_m_val > 0 and not np.isinf(sigma_S_per_m_val) and not np.isnan(sigma_S_per_m_val):
            ln_sigma_results.append(np.log(sigma_S_per_m_val))
        else:
            ln_sigma_results.append(np.nan) # Use NaN for invalid log inputs
            
    # --- Section 2: Convert Lists to NumPy Arrays for Efficient Operations and Plotting ---
    T_array_K_results = np.array(temp_results_K)
    ln_n_array = np.array(ln_n_results)
    inv_T_array_per_K = np.array(inv_T_results_per_K)
    Ef_array_eV = np.array(Ef_results_eV)
    mu_L_array_m2_per_Vs = np.array(mu_L_results_m2_per_Vs)
    mu_I_array_m2_per_Vs = np.array(mu_I_results_m2_per_Vs)
    mu_total_array_m2_per_Vs = np.array(mu_total_results_m2_per_Vs)
    ln_sigma_array = np.array(ln_sigma_results)
    n_array_per_m3 = np.array(n_results_per_m3)
    sigma_array_S_per_m = np.array(sigma_results_S_per_m)

    # --- Section 3: Print Summary of Array Calculations and Example Values ---
    print("Calculations over temperature range complete. Data stored in NumPy arrays.")
    # Find index closest to 300K in the calculated temperature array for a sample printout
    idx_300K_main_loop = np.argmin(np.abs(T_array_K_results - 300.0))
    if idx_300K_main_loop < len(n_array_per_m3): # Check if index is valid
        print(f"\nExample values from main loop array at T ~ {T_array_K_results[idx_300K_main_loop]:.2f} K:")
        print(f"  Electron concentration n = {n_array_per_m3[idx_300K_main_loop]:.3e} m^-3")
        print(f"  Conductivity sigma = {sigma_array_S_per_m[idx_300K_main_loop]:.3e} S/m")
        print(f"  Fermi Level E_F = {Ef_array_eV[idx_300K_main_loop]:.3f} eV (from Ev=0)")
        print(f"  Total mobility mu_total = {mu_total_array_m2_per_Vs[idx_300K_main_loop]:.4f} m^2/(V·s)")

    # --- Section 4: Specific Calculations and Printout for T = 300 K ---
    print("\n--- Calculated Parameters at T = 300 K (Specific Calculation) ---")
    T_calc_K = 300.0 # Specific temperature for detailed parameter calculation

    # Recalculate parameters at T_calc_K for precise values
    E_F_300K_eV, n_300K_per_m3, N_D_plus_300K_per_m3 = calculate_fermi_level_and_carriers_n_type(
        T_calc_K, Eg0_GaAs_eV, alpha_Eg_GaAs_eV_per_K, beta_Eg_GaAs_K,
        m_e_star_GaAs_kg, m_dp_star_GaAs_kg, Nd_GaAs_per_m3, Ed_GaAs_eV, g_D_GaAs,
        k_B_eV_per_K, k_B_J_per_K, h_Js
    )
    Eg_300K_eV = calculate_Eg_eV(T_calc_K, Eg0_GaAs_eV, alpha_Eg_GaAs_eV_per_K, beta_Eg_GaAs_K)
    mu_L_300K_m2_per_Vs = calculate_lattice_mobility_electron_m2_per_Vs(
        T_calc_K, mu_L0_GaAs_m2_per_Vs, s_L_GaAs
    )
    mu_I_300K_m2_per_Vs = calculate_ionized_impurity_mobility_electron_m2_per_Vs(
        T_calc_K, n_300K_per_m3, N_D_plus_300K_per_m3, m_e_star_GaAs_kg, epsilon_s_GaAs_relative,
        k_B_J_per_K, epsilon_0_F_per_m, q_C, hbar_Js
    )
    mu_total_300K_m2_per_Vs = calculate_total_mobility_electron_m2_per_Vs(
        mu_L_300K_m2_per_Vs, mu_I_300K_m2_per_Vs
    )
    sigma_300K_S_per_m = calculate_conductivity_S_per_m(
        n_300K_per_m3, mu_total_300K_m2_per_Vs
    )

    # Print calculated parameters at 300 K
    print(f"Electron Mobility (μ_total): {mu_total_300K_m2_per_Vs * 10000:.2f} cm²/Vs")
    print(f"Electrical Conductivity (σ): {sigma_300K_S_per_m:.2e} S/m  ({sigma_300K_S_per_m / 100:.2e} S/cm)")

    # Hall Coefficient (R_H)
    if n_300K_per_m3 > 0: # Avoid division by zero if n is zero
        R_H_300K_m3_per_C = -r_H_GaAs_300K / (n_300K_per_m3 * q_C) # R_H = -r_H / (n*q) for n-type
        print(f"Hall Coefficient (R_H): {R_H_300K_m3_per_C:.3e} m³/C  ({R_H_300K_m3_per_C * 1e6:.2f} cm³/C)")
    else:
        print("Hall Coefficient (R_H): Not calculable (n_300K_per_m3 is zero or invalid)")
        R_H_300K_m3_per_C = np.nan # Set to NaN for subsequent calculations if needed

    # Thermal Conductivity (κ)
    r_eff_300K = 0.0  # Assumed effective scattering parameter for Lorenz number (simplification)
    # Lorenz number L = (k_B/q)^2 * (r_eff + 2.5) for non-degenerate case, using Ac for (r_eff+2.5) from Seebeck
    # Ac_seebeck_GaAs_dimensionless is (r_s + 2.5). Assuming r_s = r_eff_300K for consistency here.
    L_300K = (k_B_J_per_K / q_C)**2 * Ac_seebeck_GaAs_dimensionless # Lorenz number in WΩK⁻² (using Ac for (r_s+2.5))
    kappa_e_300K_W_per_mK = L_300K * sigma_300K_S_per_m * T_calc_K # Electronic thermal conductivity (κ_e)
    kappa_L_300K_calc_W_per_mK = calculate_lattice_thermal_conductivity_W_per_mK( # Lattice thermal conductivity (κ_L)
        T_calc_K, kappa_L_300_GaAs_W_per_mK, s_kappa_GaAs
    )
    kappa_total_300K_W_per_mK = kappa_e_300K_W_per_mK + kappa_L_300K_calc_W_per_mK # Total thermal conductivity
    print(f"Thermal Conductivity (κ_total): {kappa_total_300K_W_per_mK:.3f} W/(m·K)  ({kappa_total_300K_W_per_mK / 100:.3f} W/(cm·K))")
    print(f"  Electronic Component (κ_e): {kappa_e_300K_W_per_mK:.3f} W/(m·K)")
    print(f"  Lattice Component (κ_L): {kappa_L_300K_calc_W_per_mK:.3f} W/(m·K)")

    # Seebeck Coefficient (S)
    # S = -(k_B/q) * ( (E_c - E_F)/(k_B*T) + Ac )
    # Here, E_F_300K_eV is referenced from E_v=0. Eg_300K_eV is E_c (since E_v=0).
    # So, (Eg_300K_eV - E_F_300K_eV) correctly represents (E_c - E_F_from_Ev).
    reduced_fermi_potential_Ec = (Eg_300K_eV - E_F_300K_eV) / (k_B_eV_per_K * T_calc_K) # (E_c - E_F)/(kT)
    S_300K_V_per_K = -(k_B_J_per_K / q_C) * ( reduced_fermi_potential_Ec + Ac_seebeck_GaAs_dimensionless )
    print(f"Seebeck Coefficient (S): {S_300K_V_per_K * 1e6:.2f} μV/K")

    # Ettingshausen Effect (P_E)
    # Nernst coefficient Q_N = - (k_B/q) * mu_H * r_s, where mu_H is Hall mobility.
    # Assumed scattering parameter r_s (r_eff_300K) = 0.0 for this calculation.
    # Hall mobility mu_H = r_H * mu_drift (mu_total_300K_m2_per_Vs is drift mobility)
    Q_N_300K = -(k_B_J_per_K / q_C) * (mu_total_300K_m2_per_Vs * r_H_GaAs_300K) * r_eff_300K # r_eff_300K=0 makes Q_N=0
    
    if kappa_total_300K_W_per_mK != 0 and not np.isnan(kappa_total_300K_W_per_mK): # Avoid division by zero
        P_E_300K = (Q_N_300K * T_calc_K) / kappa_total_300K_W_per_mK
    else: # Handle cases where kappa_total might be zero or NaN
        P_E_300K = np.nan if Q_N_300K != 0 else 0.0 # If Q_N is 0, P_E is 0 unless kappa is also 0/NaN

    print(f"Ettingshausen Coefficient (P_E): {P_E_300K:.3e} K·m/Wb") # Units: K·m/Wb or K·m/(V·s)
    print("Note: Ettingshausen effect calculation uses an assumed scattering parameter r_eff=0, making P_E = 0.")
    print("The contribution of the Ettingshausen effect to Hall voltage is complex and depends on experimental setup.")


    # --- Section 5: Plotting Results ---
    # Plot 1: ln(n) vs. 1/T
    plt.figure(figsize=(8, 6))
    plt.plot(inv_T_array_per_K, ln_n_array, marker='o', linestyle='-')
    plt.xlabel("Inverse Temperature (1/K)")
    plt.ylabel("ln(n) (ln(m^-3))")
    plt.title("Electron Concentration (n-type GaAs) vs. Inverse Temperature")
    plt.grid(True)

    # Plot 2: Fermi Level (E_F), Conduction Band Edge (E_c), Valence Band Edge (E_v) vs. T
    plt.figure(figsize=(8, 6))
    Eg_array_eV = np.array([calculate_Eg_eV(T, Eg0_GaAs_eV, alpha_Eg_GaAs_eV_per_K, beta_Eg_GaAs_K) for T in T_array_K_results])
    plt.plot(T_array_K_results, Ef_array_eV, label="E_F (Fermi Level)", marker='.')
    plt.plot(T_array_K_results, Eg_array_eV, label="E_c (Conduction Band Edge)", linestyle='--')
    plt.plot(T_array_K_results, np.zeros_like(T_array_K_results), label="E_v (Valence Band Edge, E_v=0)", linestyle='--')
    plt.xlabel("Temperature (K)")
    plt.ylabel("Energy (eV)")
    plt.title("Fermi Level and Band Edges (n-type GaAs) vs. Temperature")
    plt.legend()
    plt.grid(True)

    # Plot 3: Mobilities (μ_total, μ_L, μ_I) vs. T
    plt.figure(figsize=(8, 6))
    plt.plot(T_array_K_results, mu_total_array_m2_per_Vs * 10000, label="μ_total (Total)", marker='.') # Convert m^2/Vs to cm^2/Vs
    plt.plot(T_array_K_results, mu_L_array_m2_per_Vs * 10000, label="μ_L (Lattice)", linestyle='--')
    plt.plot(T_array_K_results, mu_I_array_m2_per_Vs * 10000, label="μ_I (Ionized Impurity)", linestyle=':')
    plt.xlabel("Temperature (K)")
    plt.ylabel("Mobility (cm²/Vs)")
    plt.yscale('log') # Use logarithmic scale for mobility
    plt.title("Electron Mobility (n-type GaAs) vs. Temperature")
    plt.legend()
    plt.grid(True, which="both", ls="-") # Grid for major and minor ticks on log scale

    # Plot 4: ln(σ) vs. 1/T
    plt.figure(figsize=(8, 6))
    plt.plot(inv_T_array_per_K, ln_sigma_array, marker='x', linestyle='-')
    plt.xlabel("Inverse Temperature (1/K)")
    plt.ylabel("ln(σ) (ln(S/m))")
    plt.title("Electrical Conductivity (n-type GaAs) vs. Inverse Temperature")
    plt.grid(True)

    plt.tight_layout() # Adjust plot layout to prevent overlapping titles/labels
    plt.show() # Display all generated plots

```
