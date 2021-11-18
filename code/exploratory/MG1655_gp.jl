using StanSample
path = @__DIR__
println(path)
gp_stan = open(path * "/gp_stan.txt") do file
    read(file, String)
end

sm = SampleModel("gaussian_process", gp_stan)



#=
function run_stan(sm, df, strain, tc)
    sub_df = df[(df.tc .== tc) .& (df.strain .== strain) , :]
    println(sub_df)
    analyzed_df = DataFrame(strain=String[], well=String[], tc=Float64[], λ_max=Float64[])
    
    for (well, date) in collect(Iterators.product(sub_df.well |> unique, sub_df.date |> unique))
        for_df = sub_df[(sub_df.tc .== tc) .& (sub_df.strain .== strain) , :]
        sort!(for_df, :time_min)

        x = for_df[(for_df.well .== well) , "time_min"]
        y = for_df[(for_df.well .== well), "OD600"]

        data = Dict(
            "N" => length(x),
            "t"=> x,
            "y"=> y, 
            "N_predict"=> length(x),  
            "t_predict"=> x, 
            "alpha_param"=> [0, 1], 
            "sigma_param"=> [0, 1], 
            "rho_param"=> [1000, 50], 
        )

        rc = stan_sample(sm; data, num_chains=2);
        st = read_samples(sm)
        dy = filter(x -> occursin("dy",String(x)), names(st))
        mean_dy = [mean(st[x]) for x in dy]
        _df = DataFrame(
            strain=String[strain], 
            well=String[well], 
            tc=Float64[tc], 
            λ_max=Float64[maximum(mean_dy)], 
        )
        append!(analyzed_df, _df)
    end
    analyzed_df
end

#analyzed_df = DataFrame(strain=String[], well=String[], tc=Float64[], λ_max=Float64[])#, dy=[])

sm = SampleModel("gaussian_process", gp_stan)
#run_stan(sm, df, "MG1655", 0)=#