SELECT 
    M.Title AS MovieTitle,
    G.GenreName,
    S.SessionDate,
    C.FirstName,
    C.LastName,
    C.City,
    S.TicketPrice
FROM Tickets T
JOIN Sessions S ON T.SessionID = S.SessionID
JOIN Movies M ON S.MovieID = M.MovieID
JOIN Genres G ON M.GenreID = G.GenreID
JOIN Customers C ON T.CustomerID = C.CustomerID
WHERE T.CustomerID IN (
    SELECT CustomerID
    FROM Tickets
    GROUP BY CustomerID
    HAVING COUNT(DISTINCT SessionID) >= 2
)
ORDER BY S.SessionDate;
