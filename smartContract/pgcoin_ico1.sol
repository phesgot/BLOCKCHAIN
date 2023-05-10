pragma solidity ^0.4.11;
 
contract pgcoin_ico {
 
    //número máximo de pgcoin disponíveis no ICO		 
    uint public max_pgcoin = 1000000;
    //Taxa cotacao do hadcoin por dolar	
    uint public usd_to_pgcoin = 1000;
    //total de pgcoin compradas por investidores	
    uint public total_pgcoin_bought = 0;
    
    //funcoes de equivalencia
    mapping(address => uint) equity_pgcoin;
    mapping(address => uint) equity_usd;
 
    //verificando se o investidor por comprar pgcoin
    modifier can_buy_pgcoin(uint usd_invested) {
        require (usd_invested * usd_to_pgcoin + total_pgcoin_bought <= max_pgcoin);
        _;
    }
 
    //retorna o valor do investimento em pgcoin 	
    function equity_in_pgcoin(address investor) external constant returns (uint){
        return equity_pgcoin[investor];
    }
 
    //retorna o valor do investimento em dolares
    function equity_in_usd(address investor) external constant returns (uint){
        return equity_usd[investor];
    }
 
    //compra de pgcoin 
    function buy_pgcoin(address investor, uint usd_invested) external 
    can_buy_pgcoin(usd_invested) {
        uint pgcoin_bought = usd_invested * usd_to_pgcoin;
        equity_pgcoin[investor] += pgcoin_bought;
        equity_usd[investor] = equity_pgcoin[investor] / 1000;
        total_pgcoin_bought += pgcoin_bought;
    }
 
    //venda de pgcoin
    function sell_pgcoin(address investor, uint pgcoin_sold) external {
        equity_pgcoin[investor] -= pgcoin_sold;
        equity_usd[investor] = equity_pgcoin[investor] / 1000;
        total_pgcoin_bought -= pgcoin_sold;
    }
}
