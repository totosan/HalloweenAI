FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY ["src/FaceMgt/BlazorApp/BlazorApp.csproj", "."]
RUN dotnet restore "BlazorApp.csproj"
COPY src/FaceMgt/BlazorApp/ .
RUN dotnet build "BlazorApp.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "BlazorApp.csproj" -c Release -o /app/publish

FROM base AS final
ARG REDIS_CONN_STR
ENV REDIS_CONN_STR=$REDIS_CONN_STR
ARG REDIS_KEY
ENV REDIS_KEY=$REDIS_KEY

WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "BlazorApp.dll"]