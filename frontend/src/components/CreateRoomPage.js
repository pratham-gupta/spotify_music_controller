import React , {Component} from "react";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import { Link } from "react-router-dom";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel  from "@material-ui/core/FormControlLabel";
import { Collapse } from "@material-ui/core";
import Alert from "@material-ui/lab/Alert"



export default class CreateRoomPage extends Component{
  
    static defaultProps = {
        votesToSkip : 2,
        guestCanPause : true,
        update : false,
        roomCode : null,
        updateCallback : () => {},

    };


    constructor(props){
        super(props);
        this.state = {
            guestCanPause : this.props.guestCanPause,
            votesToSkip : this.props.votesToSkip,
            errorMsg : "",
            successMsg :"",
            updateCallback: () => {},
            
        };
        this.handleRoomButtonPressed = this.handleRoomButtonPressed.bind(this);
        this.handleGuestCanPauseChange = this.handleGuestCanPauseChange.bind(this);
        this.handleVotesChange = this.handleVotesChange.bind(this);
        this.renderCreateRoomButton = this.renderCreateRoomButton.bind(this);
        this.renderUpdateButton = this.renderUpdateButton.bind(this);
        this.handleUpdateButtonPressed = this.handleUpdateButtonPressed.bind(this);
    }



    renderUpdateButton(){
        return(
            
            <Grid item xs={12} align='center' spacing={0}>
                
              
                
                <Button color="secondary" onClick={this.handleUpdateButtonPressed} variant="contained">
                    Update Room
                </Button>
                </Grid>
            
        )
    }

    renderCreateRoomButton(){
        return(
            <Grid container spacing={1}>
                <Grid container item xs={12} align='center' spacing={0}>
            <Grid item xs={12} align='center' spacing={0}>
                
                <Button color="secondary" variant="contained" to='/' component = {Link}>
                    Back
                </Button>
               
                
                <Button color="primary" onClick={this.handleRoomButtonPressed} variant="contained">
                    Create new Room
                </Button>
                </Grid>
            </Grid>
            </Grid>
        )
    }

    handleVotesChange(e){
        this.setState({
            votesToSkip : e.target.value,
        });
    }

    handleGuestCanPauseChange(e){
        this.setState({
            guestCanPause: e.target.value === 'true' ? true : false,
        });
    }

    handleRoomButtonPressed(){
        // console.log(this.state);
        const requestOptions = {
            method:"POST",
            headers :{'Content-type':"application/json"},
            body : JSON.stringify({
                votes_to_skip : this.state.votesToSkip,
                guest_can_pause : this.state.guestCanPause,
            }),
        };
        fetch('/api/create-room',requestOptions).then((response) => response.json()
        ).then((data) => this.props.history.push("/room/" + data.code));

    }

    handleUpdateButtonPressed(){
        const requestOptions = {
            method : "PATCH",
            headers : {"Content-Type":"application/json"},
            body : JSON.stringify({
                votes_to_skip : this.state.votesToSkip,
                guest_can_pause : this.state.guestCanPause,
                code: this.props.roomCode
            }),

        };
        fetch('/api/update-room',requestOptions).then((response) => {
            if(response.ok){
                this.setState({
                   successMsg : "Room Updated Successfully !" 
                })
            }else{
                this.setState({
                    errorMsg : "Error Updating room ...."
                })

            }
            this.props.updateCallback();
        })
        

    }



    render(){
        const title = this.props.update ? "Update Room" : "Create a Room"
    return (
        <Grid container spacing = {5} >
           
           <Grid item xs={12} align="center">
                
                <Collapse in = {this.state.errorMsg != "" || this.state.successMsg != ""}>
                    {this.state.successMsg != "" ? <Alert severity="success" 
                    onClose={() => this.setState({successMsg:""})}>{this.state.successMsg}</Alert> :<Alert severity="error" 
                    onClose={() => this.setState({successMsg:""})}>{this.state.errorMsg}</Alert>}
                </Collapse>
                
                </Grid>

            <Grid item xs={12} align="center">
                
            <Typography component = "h4" variant="h4">
                {title}
                </Typography>
            
            </Grid>

            <Grid item xs={12} align="center">
            <FormControl component = 'fieldset'>
                <FormHelperText>
                    <div align="center">Guest Control of Playback state</div>
                </FormHelperText>
                <RadioGroup row defaultValue = {this.props.guestCanPause.toString()} onChange={this.handleGuestCanPauseChange}>
                    <FormControlLabel value="true" control = {<Radio color='primary' />}
                            label = "Play/Pause"
                            labelPlacement = "bottom" /> 
                    <FormControlLabel value="false" control = {<Radio color='secondary' />}
                            label = "No Control"
                            labelPlacement = "bottom" /> 



                </RadioGroup>
            </FormControl>
            
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl component='fieldset'>
                    <TextField id='outlined-basic' required={true} type='number'
                     defaultValue = {this.state.votesToSkip} 
                     onChange = {this.handleVotesChange}
                     variant='outlined'
                     inputProps = {{min:1,
                                    style : {textAlign : "center"} }}
                     ></TextField>
                     <FormHelperText>
                         <div align='center'>
                           Votes Required To Skip Song.
                         </div>

                     </FormHelperText>
                </FormControl>
            </Grid>
            {this.props.update ? this.renderUpdateButton() : this.renderCreateRoomButton()}
            
            </Grid>
 
    );
    }
}