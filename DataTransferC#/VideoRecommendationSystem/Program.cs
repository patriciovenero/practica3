using System;
using StackExchange.Redis;
using MongoDB.Driver;
using Newtonsoft.Json;
using MongoDB.Bson;

namespace VideoRecommendationSystem
{
    class Program
    {
        static void Main(string[] args)
        {
            // Configuración de Redis
            string redisConnectionString = "localhost:6379";
            ConnectionMultiplexer redis = ConnectionMultiplexer.Connect(redisConnectionString);
            IDatabase redisDb = redis.GetDatabase();

            // Configuración de MongoDB
            string mongoConnectionString = "mongodb://localhost:27017";
            MongoClient mongoClient = new MongoClient(mongoConnectionString);
            IMongoDatabase mongoDatabase = mongoClient.GetDatabase("recomendacionesdevideos");
            IMongoCollection<BsonDocument> infoVideoCollection = mongoDatabase.GetCollection<BsonDocument>("infovideo");

            // Recuperar la información de Redis y guardarla en MongoDB
            RedisKey[] keys = redis.GetServer(redisConnectionString).Keys(pattern: "*").ToArray();
            foreach (var key in keys)
            {
                RedisValue value = redisDb.StringGet(key);
                string json = value.ToString();

                // Parsear el JSON y guardar en MongoDB
                BsonDocument document = BsonDocument.Parse(json);
                infoVideoCollection.InsertOne(document);
            }

            Console.WriteLine("Proceso completado: Se transfirió la información de Redis a MongoDB.");
        }
    }
}
