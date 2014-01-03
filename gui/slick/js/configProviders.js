$(document).ready(function(){

    $.fn.showHideProviders = function() {
        $('.providerDiv').each(function(){
            var providerName = $(this).attr('id');
            var selectedProvider = $('#editAProvider :selected').val();

            if (selectedProvider+'Div' == providerName)
                $(this).show();
            else
                $(this).hide();

        });
    } 

    $.fn.addProvider = function (id, name, url, key, isDefault, showProvider) {

        if (url.match('/$') == null)
            url = url + '/'

        var newData = [isDefault, [name, url, key]];
        newznabProviders[id] = newData;

        if (!isDefault)
        {
            $('#editANewznabProvider').addOption(id, name);
            $(this).populateNewznabSection();
        }

        if ($('#provider_order_list > #'+id).length == 0 && showProvider != false) {
            var toAdd = '<li class="ui-state-default" id="'+id+'"> <input type="checkbox" id="enable_'+id+'" class="provider_enabler" CHECKED> <a href="'+url+'" class="imgLink" target="_new"><img src="'+sbRoot+'/images/providers/newznab.gif" alt="'+name+'" width="16" height="16"></a> '+name+'</li>'

            $('#provider_order_list').append(toAdd);
            $('#provider_order_list').sortable("refresh");
        }

        $(this).makeNewznabProviderString();

    }

    $.fn.updateProvider = function (id, url, key) {

        newznabProviders[id][1][1] = url;
        newznabProviders[id][1][2] = key;

        $(this).populateNewznabSection();

        $(this).makeNewznabProviderString();
    
    }

    $.fn.deleteProvider = function (id) {
    
        $('#editANewznabProvider').removeOption(id);
        delete newznabProviders[id];
        $(this).populateNewznabSection();

        $('#provider_order_list > #'+id).remove();

        $(this).makeNewznabProviderString();

    }

    $.fn.populateNewznabSection = function() {

        var selectedProvider = $('#editANewznabProvider :selected').val();

        if (selectedProvider == 'addNewznab') {
            var data = ['','',''];
            var isDefault = 0;
            $('#newznab_add_div').show();
            $('#newznab_update_div').hide();
        } else {
            var data = newznabProviders[selectedProvider][1];
            var isDefault = newznabProviders[selectedProvider][0];
            $('#newznab_add_div').hide();
            $('#newznab_update_div').show();
        }

        $('#newznab_name').val(data[0]);
        $('#newznab_url').val(data[1]);
        $('#newznab_key').val(data[2]);
        
        if (selectedProvider == 'addNewznab') {
            $('#newznab_name').removeAttr("disabled");
            $('#newznab_url').removeAttr("disabled");
        } else {

            $('#newznab_name').attr("disabled", "disabled");

            if (isDefault) {
                $('#newznab_url').attr("disabled", "disabled");
                $('#newznab_delete').attr("disabled", "disabled");
            } else {
                $('#newznab_url').removeAttr("disabled");
                $('#newznab_delete').removeAttr("disabled");
            }
        }

    }
    
    $.fn.makeNewznabProviderString = function() {

        var provStrings = new Array();
        
        for (var id in newznabProviders) {
            provStrings.push(newznabProviders[id][1].join('|'));
        }

        $('#newznab_string').val(provStrings.join('!!!'))

    }
    
    $.fn.refreshProviderList = function() {
            var idArr = $("#provider_order_list").sortable('toArray');
            var finalArr = new Array();
            $.each(idArr, function(key, val) {
                    var checked = + $('#enable_'+val).prop('checked') ? '1' : '0';
                    finalArr.push(val + ':' + checked);
            });

            $("#provider_order").val(finalArr.join(' '));
    }

    $.fn.hideConfigTab = function () {

      $("#config-components").tabs( "disable", 1 );
      $("#config-components ul li:eq(1)").hide();

    };

    $.fn.showProvidersConfig = function () {

    $("#provider_order_list li").each(function( index ) {

      if ($(this).find("input").attr("checked")) {
        $(this).addTip();
        } else {
          $(this).qtip('destroy');
        }
      });
    };

  $.fn.addTip = function() {

      var config_id = $(this).find("input").attr('id').replace("enable_", "") + "Div";
      var config_form = '<div id="config"><form id="configForm_tip" action="saveProviders" method="post"><fieldset class="component-group-list tip_scale"><div class="providerDiv_tip">' + $("div[id*="+config_id+"]").html() + '</div></fieldset></form></div>'
      var provider_name =  $.trim($(this).text()).replace('*','')
  
      if ($("div[id*="+config_id+"]").length == 0) {
        return false
      }
  
      $(this).qtip({
  
          overwrite: true,
          position: {
             adjust: {
                x: 0, y: 0,
             },
             my: 'left top',
               at: 'top right',
          },
          show: {
               event: 'mouseenter', // Show it on click...
               target: false,
               solo: true,
               delay: 90,
               effect: true,
          },
          hide: {
               fixed: true,
               delay: 900,
          },
          content: {
          text: config_form,
                title: {
                    text: provider_name + ' Config',
                    button: true
                }
          },
          style: {
              border: {
                  width: 5,
                  radius: 2,
                  color: '#e1e1e1'
              },
              width: 350,
              background: '#FFF',
              padding: 15,
              tip: true, // Give it a speech bubble tip with automatic corner detection
              classes: 'qtip-dark qtip-shadow',
          },
      });

    }

    var newznabProviders = new Array();

    $('.newznab_key').change(function(){

        var provider_id = $(this).attr('id');
        provider_id = provider_id.substring(0, provider_id.length-'_hash'.length);

        var url = $('#'+provider_id+'_url').val();
        var key = $(this).val();

        $(this).updateProvider(provider_id, url, key);

    });
    
    $('#newznab_key,#newznab_url').change(function(){
        
        var selectedProvider = $('#editANewznabProvider :selected').val();

        var url = $('#newznab_url').val();
        var key = $('#newznab_key').val();
        
        $(this).updateProvider(selectedProvider, url, key);
        
    });
    
    $('#editAProvider').change(function(){
        $(this).showHideProviders();
    });

    $('#editANewznabProvider').change(function(){
        $(this).populateNewznabSection();
    });
    
    $('.provider_enabler').live('click', function(){
        $(this).refreshProviderList();
    }); 
    

    $('#newznab_add').click(function(){
        
        var selectedProvider = $('#editANewznabProvider :selected').val();
        
        var name = $.trim($('#newznab_name').val());
        var url = $.trim($('#newznab_url').val());
        var key = $.trim($('#newznab_key').val());
        
        if (!name)
        	return;

        if (!url)
        	return;        	

        if (!key)
        	return;

        var params = {name: name};
        
        // send to the form with ajax, get a return value
        $.getJSON(sbRoot + '/config/providers/canAddNewznabProvider', params,
            function(data){
                if (data.error != undefined) {
                    alert(data.error);
                    return;
                }

                $(this).addProvider(data.success, name, url, key, 0);
        });


    });

    $('.newznab_delete').click(function(){
    
        var selectedProvider = $('#editANewznabProvider :selected').val();

        $(this).deleteProvider(selectedProvider);

    });

    $('#torrentrss_add').click(function(){
        var selectedProvider = $('#editATorrentRssProvider :selected').val();

        var name = $('#torrentrss_name').val();
        var url = $('#torrentrss_url').val();
        var params = { name: name, url: url}

        // send to the form with ajax, get a return value
        $.getJSON(sbRoot + '/config/providers/canAddTorrentRssProvider', params,
            function(data){
                if (data.error != undefined) {
                    alert(data.error);
                    return;
                }

                $(this).addTorrentRssProvider(data.success, name, url);
        });
    });

    $('.torrentrss_delete').on('click', function(){
        var selectedProvider = $('#editATorrentRssProvider :selected').val();
        $(this).deleteTorrentRssProvider(selectedProvider);
    });


    $(this).on('change', "[class='providerDiv_tip'] input", function(){
        $('div .providerDiv ' + "[name=" + $(this).attr('name') + "]").replaceWith($(this).clone());
        $('div .providerDiv ' + "[newznab_name=" + $(this).attr('id') + "]").replaceWith($(this).clone());
    });

    $(this).on('change', "[class='providerDiv_tip'] select", function(){

    $(this).find('option').each( function() {
      if ($(this).is(':selected')) {
        $(this).prop('defaultSelected', true)
      } else {
        $(this).prop('defaultSelected', false);
      }
    });

    $('div .providerDiv ' + "[name=" + $(this).attr('name') + "]").empty().replaceWith($(this).clone())});

    $(this).on('change', '.enabler', function(){
      if ($(this).is(':checked')) {
          $('.content_'+$(this).attr('id')).each( function() {
              $(this).show()
          })
      } else {
            $('.content_'+$(this).attr('id')).each( function() {
                $(this).hide()
            })
      }
    });

    $(".enabler").each(function(){
        if (!$(this).is(':checked')) {
          $('.content_'+$(this).attr('id')).hide();
        } else {
          $('.content_'+$(this).attr('id')).show();
      }
    });

    $.fn.makeTorrentOptionString = function(provider_id) {

	    var seed_ratio  = $('.providerDiv_tip #'+provider_id+'_seed_ratio').prop('value');
	    var seed_time   = $('.providerDiv_tip #'+provider_id+'_seed_time').prop('value');
	    var process_met = $('.providerDiv_tip #'+provider_id+'_process_method').prop('value');
		var option_string = $('.providerDiv_tip #'+provider_id+'_option_string');	

        option_string.val([seed_ratio, seed_time, process_met].join('|'))

    }

    $(this).on('change', '.seed_option', function(){

        var provider_id = $(this).attr('id').split('_')[0];

		$(this).makeTorrentOptionString(provider_id);

    });

    // initialization stuff

    $(this).hideConfigTab();

    $(this).showHideProviders();

    $(this).showProvidersConfig();

    $("#provider_order_list").sortable({
        placeholder: 'ui-state-highlight',
        update: function (event, ui) {
            $(this).refreshProviderList();
        }
    });

    $("#provider_order_list").disableSelection();

});