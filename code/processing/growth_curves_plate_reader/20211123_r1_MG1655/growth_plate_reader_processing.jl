import  XLSX, CSV, Dates, ColorSchemes
using Statistics, Jedi, CairoMakie, DataFrames
CairoMakie.activate!()

Jedi.styles.default_makie!()
##
dir = @__DIR__
home_dir = joinpath(split(dir, '/')[1:end-4]...)

# Find date
workdir = split(dir, '/')[end]
DATE = parse(Int64, split(workdir, '_')[1])
RUN_NO = parse(Int64, split(workdir, '_')[2][end])
##
# Load the data.
file = "/$(home_dir)/data/plate_reader/$workdir.txt"

xf = XLSX.readxlsx(dir * "/$(DATE)_plate_layout.xlsx")

meta_df = DataFrames.DataFrame()

for table in XLSX.sheetnames(xf)
    flattened = vec(hcat(XLSX.getdata(xf[table])...))
    DataFrames.insertcols!(meta_df, table => flattened)
end
meta_df = sort(meta_df, :well)
##

measurements = CSV.read(file, DataFrames.DataFrame, header=false)
time_points = measurements[!, "Column1"]
time_points = Dates.second.(time_points) ./60 .+ Dates.minute.(time_points) .+ 60 .* Dates.hour.(time_points)
temperatures = measurements[!, "Column2"]

df = DataFrames.DataFrame()

for i in 3:size(measurements)[2]
    OD = measurements[!, i]
    _df = DataFrames.DataFrame(time_min=time_points, temp=temperatures, OD600=OD)
    for column in names(meta_df)
        DataFrames.insertcols!(_df, column => meta_df[i-2, column])
    end

    append!(df, DataFrames.dropmissing(_df))
end

# Blank normalization
df_blank = df[df.strain .== "blank", :]
gdf = DataFrames.groupby(df_blank, :time_min)
mean_blank_df = combine(gdf, :OD600 => (x -> (OD_mean=mean(x), OD_std=std(x))) => AsTable)
df = df[df.strain .!= "blank", :]
gdf = DataFrames.groupby(df, :well)
df = transform(gdf, :OD600 => (x -> (OD600_norm = x .- mean_blank_df[!, "OD_mean"])))
rename!(df, Dict("OD600_function" => "OD600_norm"))

##

# Check if output directory exists
if ~ispath("$dir/output") 
    mkdir("$dir/output")
end

# Save output
CSV.write("$dir/output/$(DATE)_r$(RUN_NO)_growth_plate.csv", df)

# Make plot

fig = Figure()
ax1 = Axis(fig[1, 1])
ax1.xlabel = "time [min]"
ax1.ylabel = "normalized OD600"

df_means = DataFrames.DataFrame()

for (strain, color) in zip(df.strain |> unique, ColorSchemes.seaborn_colorblind)
    sub_df = df[df.strain .== strain, :]
    for pos_sel in sub_df.pos_selection |> unique
        sub_sub_df = sub_df[sub_df.pos_selection .== pos_sel, :]
        _gdf = DataFrames.groupby(sub_sub_df, :time_min)
        mean_df = combine(_gdf, :OD600_norm => (x -> (OD_mean=mean(x), OD_std=std(x))) => AsTable)
        insertcols!(mean_df, "strain"=>strain, "pos_selection"=>pos_sel)
        append!(df_means, mean_df)

        lines!(ax1, mean_df.time_min, mean_df.OD_mean, label=strain)
        scatter!(ax1, mean_df.time_min, mean_df.OD_mean)
        errorbars!(ax1, mean_df.time_min, mean_df.OD_mean, mean_df.OD_std)
    end
end

CSV.write("$dir/output/$(DATE)_r$(RUN_NO)_growth_mean.csv", df_means)
axislegend(ax1, position=:lt)#, merge = merge, unique = unique)
CairoMakie.save("$dir/output/$(DATE)_r$(RUN_NO)_all_curves.pdf", fig)