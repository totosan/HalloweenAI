using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;
using BlazorApp.Data;
using StackExchange.Redis;
using static System.Environment;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddSingleton<WeatherForecastService>();

var redis_cnn = Environment.GetEnvironmentVariable("REDIS_CONN_STR");
var redis_key = Environment.GetEnvironmentVariable("REDIS_KEY");
var redis_port = Environment.GetEnvironmentVariable("REDIS_PORT");

Console.WriteLine($"Redis Connection String: {redis_cnn}:{redis_port}");

builder.Services.Configure<FACEAPI>(builder.Configuration.GetSection("FACEAPI"));

builder.Services.AddStackExchangeRedisCache(options =>
        {
            //options.Configuration = builder.Configuration.GetConnectionString("Redis");
            options.InstanceName = "BlazorApp";
        }
    );

builder.Services.AddSingleton<IConnectionMultiplexer>(sp => ConnectionMultiplexer.Connect(
    new ConfigurationOptions{ 
        EndPoints = { redis_cnn+":6379" },
        AbortOnConnectFail=true,
        //Password = redis_key,
        //Ssl = true
    }));


var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
}

app.UseStaticFiles();

app.UseRouting();

app.MapBlazorHub();
app.MapFallbackToPage("/_Host");
app.MapPost("/api/face{faceId}",(string id, FaceGroupFactory fg)=>fg.PutFaceId(id));
app.Run();