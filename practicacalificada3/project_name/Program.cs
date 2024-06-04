using System;
using System.Data;
using System.Threading.Tasks;
using Microsoft.Data.SqlClient;

namespace SqlConsoleApp
{
    class Program
    {
        static async Task Main(string[] args)
        {
            string connectionString = "Server=mssql-174495-0.cloudclusters.net,19074;Database=AdventureWorks2019;User Id=beta1;Password=Mosque12;TrustServerCertificate=True;";
            
            using (SqlConnection connection = new SqlConnection(connectionString))
            {
                await connection.OpenAsync();

                Console.WriteLine("Tablas en la base de datos:");
                await ListTablesAsync(connection);
            }
        }

        static async Task ListTablesAsync(SqlConnection connection)
        {
            string query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'";
            SqlCommand command = new SqlCommand(query, connection);

            try
            {
                using (SqlDataReader reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        Console.WriteLine(reader.GetString(0));
                    }
                }
            }
            catch (SqlException ex)
            {
                Console.WriteLine($"Error al ejecutar la consulta: {ex.Message}");
            }
        }
    }
}
