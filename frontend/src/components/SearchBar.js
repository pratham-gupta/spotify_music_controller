import React, { Component} from 'react';
import {Grid, Button, Typography,AppBar,Toolbar} from "@material-ui/core";
import TextField from "@material-ui/core/TextField";
import SearchIcon from '@material-ui/icons/Search';
import { InputBase } from '@material-ui/core';




export default class SearchBar extends Component {
   
    constructor(props) {
        super(props);
        this.state = {
            searchString : "",
            error : "",
        }
        this.searchButtonPressed = this.searchButtonPressed.bind(this);
        this.handleTextFieldChange = this.handleTextFieldChange.bind(this);
        this.iterateOverList = this.iterateOverList.bind(this);
    }



    render(){
        return(
            <Grid container spacing={2} xs={12}>
                <Grid container item xs={12} align ='center' spacing={2}>
            <div className = 'abc'> 
                <AppBar position = 'static'>
                    <Toolbar>

                        <SearchIcon />
                        {/* <InputBase
                            placeholder='search'
                            classes = {{}} /> */}
                            <TextField id='outlined-basic' required={true} type='string'
                            placeholder="Search"
                            error={this.state.error}
                            label = "Search"
                            value = {this.state.searchString}
                    
                            onChange = {this.handleTextFieldChange}
                             variant='outlined'
                            inputProps = {{min:1,
                                    style : {textAlign : "center"} }}
                     ></TextField>
                        <Button variant="contained" color="secondary" onClick = {this.searchButtonPressed} >
                                Go
                            </Button>

                    </Toolbar>

                </AppBar>
            </div>
            </Grid>
            </Grid>

        )

    }

    iterateOverList(search_list){
        for(var j=0; j < search_list.length; j++){
            console.log(search_list[j].song_name);
        }
    }

   


    searchButtonPressed(){
        console.log("search buttom pressed",this.state.searchString)
        var formdata = new FormData();
        formdata.append("query", this.state.searchString);

        var requestOptions = {
            method: 'POST',
            body: formdata,
            redirect: 'follow'
          };
        
        fetch("/spotify/search",requestOptions).then(
            (response) => response.json()
        ).then((result) => (result['list']) 
        ).then((search_list) => {for(var j=0; j < search_list.length; j++){
            console.log(search_list[j].song_name);
            }} )
    }
        
    
        
    
    handleTextFieldChange(e){
        this.setState({
            searchString : e.target.value,
        })
    }


}

