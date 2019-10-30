-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/GoTqrT
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- Modify this code to update the DB schema diagram.
-- To reset the sample schema, replace everything with
-- two dots ('..' - without quotes).

CREATE TABLE "all_vehicles" (
    "unique_id" INT   NOT NULL,
    "date" DATE   NOT NULL,
    "day" INTEGER   NOT NULL,
    "month" INTEGER   NOT NULL,
    "year" INTEGER   NOT NULL,
    "hour" INTEGER   NOT NULL,
    "day_of_week" INTEGER   NOT NULL,
    "atemp" INTEGER   NOT NULL,
    "ahum" INTEGER   NOT NULL,
    "awind" INTEGER   NOT NULL,
    "prec" INTEGER   NOT NULL,
    "vehicle_encoded" INTEGER   NOT NULL,
    "hour_encoded" INTEGER   NOT NULL,
    "month_encoded" INTEGER   NOT NULL,
    "count_encoded" INTEGER   NOT NULL,
    "count" INTEGER   NOT NULL,
    CONSTRAINT "pk_all_vehicles" PRIMARY KEY (
        "unique_id"
     )
);

CREATE TABLE "vehicles" (
    "vehicle_encoded" INTEGER   NOT NULL,
    "vehicle_type" VARCHAR(30)   NOT NULL
);

CREATE TABLE "hours" (
    "hour_encoded" INTEGER   NOT NULL,
    "hour_group" VARCHAR(30)   NOT NULL
);

CREATE TABLE "months" (
    "month_encoded" INTEGER   NOT NULL,
    "month_group" VARCHAR(30)   NOT NULL
);

CREATE TABLE "counts" (
    "count_encoded" INTEGER   NOT NULL,
    "count_group" VARCHAR(30)   NOT NULL
);

CREATE TABLE "weather" (
    "date" DATE   NOT NULL,
    "maxtemp" INTEGER   NOT NULL,
    "atemp" INTEGER   NOT NULL,
    "mintemp" INTEGER   NOT NULL,
    "maxhum" INTEGER   NOT NULL,
    "ahum" INTEGER   NOT NULL,
    "minhum" INTEGER   NOT NULL,
    "maxwind" INTEGER   NOT NULL,
    "awind" INTEGER   NOT NULL,
    "minwind" INTEGER   NOT NULL,
    "prec" INTEGER   NOT NULL,
    "day" INTEGER   NOT NULL,
    "month" INTEGER   NOT NULL,
    "day_of_week" INTEGER   NOT NULL,
    "year" INTEGER   NOT NULL
);

ALTER TABLE "vehicles" ADD CONSTRAINT "fk_vehicles_vehicle_encoded" FOREIGN KEY("vehicle_encoded")
REFERENCES "all_vehicles" ("vehicle_encoded");

ALTER TABLE "hours" ADD CONSTRAINT "fk_hours_hour_encoded" FOREIGN KEY("hour_encoded")
REFERENCES "all_vehicles" ("hour_encoded");

ALTER TABLE "months" ADD CONSTRAINT "fk_months_month_encoded" FOREIGN KEY("month_encoded")
REFERENCES "all_vehicles" ("month_encoded");

ALTER TABLE "counts" ADD CONSTRAINT "fk_counts_count_encoded" FOREIGN KEY("count_encoded")
REFERENCES "all_vehicles" ("count_encoded");

ALTER TABLE "weather" ADD CONSTRAINT "fk_weather_date" FOREIGN KEY("date")
REFERENCES "all_vehicles" ("date");

