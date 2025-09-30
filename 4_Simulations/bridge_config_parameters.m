V_positive = 85;
V_negative = -20;
V_supply = (V_positive - V_negative)/2;
 
C_load = 8*10^(-6);
%V_peak = 37.5;
f = 5000000;
 
%dV_dt = 2*pi*f*V_peak*10^(-6);
%I_load = C_load * dV_dt/(10^(-6)); %Current peak
 
% Dielectric losses: Energy being dissipated within a dielectric in the form of heat when an alternating electric field is applied
%P_load = (pi/4)*0.3*f*C_load*(V_peak*4)^2;
% For each side of the bridge:
%P_supply = (2*V_supply*I_load)/pi;
%Power dissipation
P_ampl = 100;
%P_ampl = P_supply - P_load/2;

%(pi*0.3/8)*f*C_load*16)*V_peak^2 - (4*V_supply*C_load*f)*V_peak + P_ampl = 0;

%V_peak = (32/3*pi+sqrt((32/3*pi)^2-4*8/3*pi*P_ampl/(f*C_load)))/2;
 
%% FREQUENCY RESPONSE of the amplifier with different voltages
 
% Input Parameters --------------------------------------------------------
 
    % Output current limit of the amplifier 
    %I_load = [0.2,1,2,5,10,15];
 
    % Voltage to study (v_sat_max  is the V_0 of the sinusoidal input)
    v_sat_max = 75;
    v_sat_min = 0;
    
% Simulation --------------------------------------------------------------
 
    % Load Capacitance
    %C_load = 8*10^(-6);
 
    % Frequency
    freq = logspace(2,6,50);

    P_ampl = 100;
 
    % I = C* V_0 * 2 * pi * freq
 
    for i = 1:numel(freq)
 
        V_peak(:,i) = (32/3*pi+sqrt((32/3*pi)^2-4*8/3*pi*P_ampl/(freq(i)*C_load)))/2;
 
        V_peak(:,i) = min(v_sat_max, max(v_sat_min,V_peak(:,i)));
    end

% Plot --------------------------------------------------------------------

    figure 
        for i = 1:numel(freq)
            semilogx(freq, V_peak(i)/(v_sat_max/20))
            hold on
        end
        grid on
        xlabel('Frequency (Hz)');
        ylabel('Vpeak');
        %title(['Frequency Response at ', num2str(v_sat_max * 2), ' Vpp output voltage, Imax = ', num2str(I_max),'mA' ])

